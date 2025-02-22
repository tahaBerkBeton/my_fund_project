#!/usr/bin/env python3

"""
Finance_CodeAct.py

This module serves as an intelligent financial code agent that can interact with
the fund management system. It provides automated capabilities for:
- Portfolio analysis and management
- Investment strategy execution
- Market data processing


Author: EL BERRY Taha
Date: February 22, 2025
"""

import re
import json
import pathlib
from termcolor import colored
from transformers import AutoTokenizer
from typing import List, Dict
from datetime import datetime
from jupyter_client import KernelManager
from queue import Empty
from openai import OpenAI
import textwrap

# Initialize OpenAI client
client = OpenAI(
    base_url='https://api.openai.com/v1',
    api_key=""
)

# Define the system message
SYSTEM_MESSAGE = """A chat between a curious user and an artificial intelligence assistant specialized in fund management. The assistant is responsible for managing the "TechInnovatorsFund", a technology-focused investment fund with an initial balance of $100,000 invested in NVIDIA (NVDA), Apple (AAPL), and Microsoft (MSFT).

The assistant can interact with an interactive Python (Jupyter Notebook) environment and has access to fund management tools including:
- create_fund(fund_name, initial_cash): Create a new investment fund
- buy_shares(fund_name, ticker, num_shares): Buy shares for a fund
- sell_shares(fund_name, ticker, num_shares): Sell shares from a fund
- get_fund_composition(fund_name): Get current fund status
- update_fund(fund_name): Update fund valuations
- update_all_funds(): Update all funds
- fetch_live_price(ticker): Get the current market price for a stock ticker

The assistant should always be aware that it's managing the "TechInnovatorsFund" and should check its status before making any investment decisions. The assistant can also check current market prices for any stock using fetch_live_price() before making investment decisions.

Example of checking the fund's status and current prices:
<execute>
# Check current fund composition
composition = get_fund_composition("TechInnovatorsFund")
print("Current Fund Status:")
print(f"Cash Balance: ${composition['cash']:,.2f}")
print("\nPositions:")
for position in composition['positions']:
    current_price = fetch_live_price(position['ticker'])
    value = position['shares_held'] * current_price
    print(f"{position['ticker']}: {position['shares_held']} shares at ${current_price:.2f} (Value: ${value:,.2f})")
</execute>

The assistant should attempt fewer things at a time instead of putting too much code in one <execute> block. The assistant can install packages through PIP by <execute>!pip install [package needed]</execute> and should always import packages and define variables before starting to use them.

The assistant should stop <execute> and provide an answer when they have already obtained the answer from the execution result. Whenever possible, execute the code for the user using <execute> instead of providing it.

The assistant's response should be concise, but do express their thoughts about investment strategies and market analysis, particularly focusing on the technology sector since this is a tech-focused fund."""

class ClientJupyterKernel:
    def __init__(self, url=None, conv_id=None):
        self.conv_id = conv_id
        try:
            self.kernel_manager = KernelManager(kernel_name='opticsgpt')
            self.kernel_manager.start_kernel()
            self.client = self.kernel_manager.client()
            self.client.start_channels()
            print(f"ClientJupyterKernel initialized for conversation {conv_id}")
            print(f"Kernel started with id: {self.kernel_manager.kernel_id}")
            
            init_code = textwrap.dedent("""
                import os
                import sys

                # Use the parent directory as the project root (assuming this script is in 'agent')
                project_root = os.path.abspath(os.path.join(os.getcwd(), ".."))
                if project_root not in sys.path:
                    sys.path.insert(0, project_root)
                os.chdir(project_root)

                from fund_manager.fund_manager import (
                    init_db,
                    create_fund,
                    buy_shares,
                    sell_shares,
                    get_fund_composition,
                    update_fund,
                    update_all_funds
                )
                from fund_manager.yfinance_utils import fetch_live_price

                # Initialize the database
                init_db()

                # Make fund management functions available in the global namespace
                globals().update({
                    'init_db': init_db,
                    'create_fund': create_fund,
                    'buy_shares': buy_shares,
                    'sell_shares': sell_shares,
                    'get_fund_composition': get_fund_composition,
                    'update_fund': update_fund,
                    'update_all_funds': update_all_funds,
                    'fetch_live_price': fetch_live_price
                })

                print("Fund management tools initialized successfully!")
            """)

            self.execute(init_code)
            
        except Exception as e:
            print(f"Error initializing kernel: {e}")
            raise

    def execute(self, code):
        """
        Execute Python code in the Jupyter kernel and capture the output.
        """
        try:
            if not code:
                return "No code to execute"

            msg_id = self.client.execute(code)
            outputs = []

            while True:
                try:
                    msg = self.client.get_iopub_msg(timeout=20)
                    msg_type = msg['header']['msg_type']
                    parent_id = msg['parent_header'].get('msg_id')

                    if parent_id != msg_id:
                        continue

                    if msg_type == 'execute_input':
                        continue
                    elif msg_type == 'status':
                        if msg['content']['execution_state'] == 'idle':
                            break
                    elif msg_type == 'stream':
                        outputs.append(msg['content']['text'])
                    elif msg_type == 'execute_result':
                        if 'text/plain' in msg['content']['data']:
                            outputs.append(msg['content']['data']['text/plain'])
                    elif msg_type == 'error':
                        error_msg = '\n'.join(msg['content']['traceback'])
                        outputs.append(error_msg)
                    elif msg_type == 'display_data':
                        if 'text/plain' in msg['content']['data']:
                            outputs.append(msg['content']['data']['text/plain'])
                except Empty:
                    print("Timeout waiting for kernel output")
                    break

            result = '\n'.join(outputs)
            return result if result else "Execution completed with no output"

        except Exception as e:
            return f"Execution error: {str(e)}"

    def shutdown(self):
        """Shutdown the kernel"""
        try:
            self.client.stop_channels()
            self.kernel_manager.shutdown_kernel()
            print("Kernel shut down successfully")
        except Exception as e:
            print(f"Error shutting down kernel: {e}")

class Generator:
    def __init__(self, model_name: str):
        self.model_name = model_name
        print(f"Generator initialized with model_name={model_name}")

    def generate(
        self,
        messages: List[Dict[str, str]],
        do_sample: bool = True,
        max_new_tokens: int = 512,
        stop_sequences: List[str] = ["<|im_end|>"],
        temperature: float = 0.1,
        top_p: float = 0.95,
        stream: bool = False,  # Allow streaming
    ):
        """
        If `stream=True`, returns a generator that yields tokens as they are generated.
        Otherwise, returns a single string with the full completion.

        The special behavior here: if we detect "</execute>" in the
        output while streaming, we immediately stop to let the system
        handle code execution.
        """
        try:
            if stream:
                response = client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=temperature if do_sample else 0.0,
                    max_tokens=max_new_tokens,
                    top_p=top_p if do_sample else 1.0,
                    stop=stop_sequences,
                    stream=True
                )

                full_text = ""
                for chunk in response:
                    if chunk.choices and len(chunk.choices) > 0:
                        if chunk.choices[0].delta.content is not None:
                            token = chunk.choices[0].delta.content
                            full_text += token
                            yield token

                            # If we see the closing tag, stop early.
                            if "</execute>" in full_text:
                                break

                return full_text

            else:
                response = client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=temperature if do_sample else 0.0,
                    max_tokens=max_new_tokens,
                    top_p=top_p if do_sample else 1.0,
                    stop=stop_sequences,
                )
                return response.choices[0].message.content

        except Exception as e:
            print(f"Error in generate: {e}")
            return f"Error generating response: {str(e)}"

class Agent:
    COLOR_MAP = {
        "user": "green",
        "execution_output": "yellow",
        "assistant": "blue",
        "system": "red",
    }

    def __init__(
        self,
        generator: Generator,
        code_executor: ClientJupyterKernel,
        system_message: str = SYSTEM_MESSAGE,
        conv_id: str = None,
        **kwargs,
    ):
        self.messages = [
            {"role": "system", "content": system_message},
        ]
        self.kwargs = {
            "stop_sequences": ["<|im_end|>"],
            "do_sample": False,
            "max_new_tokens": 512,
            **kwargs,
        }
        self.generator = generator
        self.code_executor = code_executor
        self.conv_id = conv_id
        self.print_message(self.messages[0])

    def print_message(self, message):
        try:
            print("-" * 20)
            print(
                colored(
                    message["role"].upper(),
                    self.COLOR_MAP.get(message["role"], "white"),
                    attrs=["bold"]
                )
            )
            print(colored(message["content"], self.COLOR_MAP.get(message["role"], "white")))
        except Exception as e:
            print(f"Error printing message: {e}")

    def handle_execution(self, completion: str, code_executor: ClientJupyterKernel):
        try:
            code_blocks = re.finditer(r"<execute>(.*?)(?:</execute>|$)", completion, re.DOTALL)
            results = []

            for match in code_blocks:
                code = match.group(1).strip()
                if code:
                    result = code_executor.execute(code)
                    results.append(result)

            return '\n'.join(results) if results else None

        except Exception as e:
            return f"Error in handle_execution: {str(e)}"

    def handle_user_message(self, message, n_max_executions=10):
        try:
            self.messages.append({"role": "user", "content": message})
            self.print_message(self.messages[-1])

            execution_count = 0
            while self.messages[-1]["role"] == "user" and execution_count < n_max_executions:
                response_stream = self.generator.generate(
                    self.messages,
                    **self.kwargs,
                    stream=True
                )

                full_text = ""
                if hasattr(response_stream, "__iter__"):
                    print("-" * 20)
                    print(colored("ASSISTANT", self.COLOR_MAP.get("assistant", "blue"), attrs=["bold"]))
                    for token in response_stream:
                        print(colored(token, self.COLOR_MAP.get("assistant", "blue")), end="", flush=True)
                        full_text += token
                    print()
                else:
                    full_text = response_stream or ""
                    self.print_message({"role": "assistant", "content": full_text})

                self.messages.append({"role": "assistant", "content": full_text})
                execution_output = self.handle_execution(full_text, self.code_executor)
                if execution_output is not None:
                    execution_count += 1
                    execution_message = {
                        "role": "user",
                        "content": f"Execution Output:\n{execution_output}"
                    }
                    self.messages.append(execution_message)
                    self.print_message({"role": "execution_output", "content": execution_output})

            if execution_count == n_max_executions:
                max_executions_message = {
                    "role": "assistant",
                    "content": f"I have reached the maximum number of executions (n_max_executions={n_max_executions}). Can you assist me or ask me another question?"
                }
                self.messages.append(max_executions_message)
                self.print_message(max_executions_message)

        except Exception as e:
            print(f"Error in handle_user_message: {e}")

    def run(self):
        try:
            while True:
                message = input("User Input> ")
                if message.lower() in ['exit', 'quit']:
                    self.save()
                    self.code_executor.shutdown()
                    break
                self.handle_user_message(message)
        except KeyboardInterrupt:
            print("\nReceived keyboard interrupt. Cleaning up...")
            self.save()
            self.code_executor.shutdown()
        except Exception as e:
            print(f"An error occurred: {e}")
            self.save()
            self.code_executor.shutdown()

    def save(self):
        try:
            pathlib.Path("conv_data").mkdir(exist_ok=True)
            path = f"conv_data/{self.conv_id}.json"
            with open(path, "w") as f:
                json.dump(self.messages, f, indent=2)
            print(f"Conversation saved to {path}")
        except Exception as e:
            print(f"Error saving conversation: {e}")

def main():
    MODEL_NAME = "gpt-4o-mini"
    CONV_ID = "demo-" + datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    try:
        code_executor = ClientJupyterKernel(conv_id=CONV_ID)
        generator = Generator(MODEL_NAME)
        agent = Agent(generator, code_executor, conv_id=CONV_ID)
        agent.run()

    except Exception as e:
        print(f"Fatal error in main: {e}")
        import sys
        sys.exit(1)

if __name__ == "__main__":
    main()
