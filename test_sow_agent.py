"""Standalone test script to run only the sow_generation_agent."""

import asyncio

from dotenv import load_dotenv

load_dotenv()

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

from sow_generator.sow_generation_agent import sow_generation_agent


async def main():
    session_service = InMemorySessionService()
    runner = Runner(
        agent=sow_generation_agent,
        app_name="sow_test",
        session_service=session_service,
    )

    session = await session_service.create_session(
        app_name="sow_test",
        user_id="test_user",
    )

    user_message = genai_types.Content(
        role="user",
        parts=[
            genai_types.Part(
                text=(
                    "Generate a SOW from the parsed proposal data at "
                    "gs://sow-generator-testing-phase/parsed-output-data/sony-1.json "
                    "and use the template at "
                    "gs://sow-generator-testing-phase/template/Copy of SOW Template.docx"
                )
            )
        ],
    )

    print("=" * 60)
    print("Starting SOW Generation Agent...")
    print("=" * 60)

    async for event in runner.run_async(
        session_id=session.id,
        user_id="test_user",
        new_message=user_message,
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(f"\n[{event.author}]: {part.text}")
                if part.function_call:
                    print(f"\n[Tool Call] {part.function_call.name}({part.function_call.args})")
                if part.function_response:
                    print(f"\n[Tool Response] {part.function_response.name}: {part.function_response.response}")

    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
