#!/usr/bin/env python
"""Script to index a codebase into the vector database."""

import argparse
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.vectordb.ingestion import index_codebase_cli


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Index codebase into vector database")
    parser.add_argument("user_id", help="User identifier (e.g., email)")
    parser.add_argument("repo_path", help="Path to repository")
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=1000,
        help="Maximum characters per chunk (default: 1000)",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing vectors before indexing",
    )

    args = parser.parse_args()

    print(f"\nIndexing codebase for user: {args.user_id}")
    print(f"Repository: {args.repo_path}")
    print(f"Chunk size: {args.chunk_size}")
    print(f"Clear existing: {args.clear}\n")

    try:
        await index_codebase_cli(
            user_id=args.user_id,
            repo_path=args.repo_path,
            chunk_size=args.chunk_size,
            clear_existing=args.clear,
        )
        print("\n✓ Indexing successful!")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
