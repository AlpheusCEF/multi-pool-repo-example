#!/usr/bin/env python3
"""
Recreate the household demo registry from seed.yaml.

Usage:
    python seed.py              # create registry in ./registry/
    python seed.py --wipe       # delete ./registry/ first, then recreate
    python seed.py --dry-run    # print what would be created, create nothing

The registry/ directory is gitignored. seed.yaml is the authoritative source.
"""

import argparse
import shutil
import sys
from pathlib import Path

import yaml

# Resolve alph from the installed package (alph-cli must be installed).
try:
    from alph.core import create_node, init_pool, init_registry
except ImportError:
    sys.exit(
        "error: alph package not found.\n"
        "Install it with: pip install -e /path/to/alph-cli"
    )

REPO_ROOT = Path(__file__).parent
SEED_FILE = REPO_ROOT / "seed.yaml"
REGISTRY_DIR = REPO_ROOT / "registry"


def load_seed() -> dict:
    with SEED_FILE.open() as f:
        return yaml.safe_load(f)


def wipe_registry() -> None:
    if REGISTRY_DIR.exists():
        shutil.rmtree(REGISTRY_DIR)
        print(f"wiped: {REGISTRY_DIR}")


def run(dry_run: bool = False) -> None:
    seed = load_seed()

    reg = seed["registry"]
    pools = seed["pools"]
    all_nodes = seed["nodes"]

    print(f"registry:  {reg['id']}  —  {reg['context'][:60]}...")
    print(f"pools:     {', '.join(pools)}")
    total_nodes = sum(len(v) for v in all_nodes.values())
    print(f"nodes:     {total_nodes} total")
    print()

    if dry_run:
        for pool_name, nodes in all_nodes.items():
            print(f"  pool/{pool_name}: {len(nodes)} nodes")
            for n in nodes:
                print(f"    [{n['node_type']}] {n['context'][:70].strip()}...")
        print("\n(dry run — nothing created)")
        return

    # Init registry
    reg_result = init_registry(
        path=REGISTRY_DIR,
        registry_id=reg["id"],
        context=reg["context"],
        name=reg.get("name", ""),
    )
    if not reg_result.valid:
        for e in reg_result.errors:
            print(f"error: {e}")
        sys.exit(1)
    print(f"created registry: {reg_result.config_path}")

    # Init pools
    for pool_name, pool_cfg in pools.items():
        pool_result = init_pool(
            registry_path=REGISTRY_DIR,
            name=pool_name,
            context=pool_cfg["context"],
            layout=pool_cfg.get("layout", "subdirectory"),
        )
        if not pool_result.valid:
            for e in pool_result.errors:
                print(f"error: {e}")
            sys.exit(1)
        print(f"created pool:     {pool_result.pool_path}")

    print()

    # Create nodes
    for pool_name, nodes in all_nodes.items():
        pool_path = REGISTRY_DIR / pool_name
        created = 0
        dupes = 0
        for node in nodes:
            result = create_node(
                pool_path=pool_path,
                source=node.get("source", "seed"),
                node_type=node.get("node_type", "fixed"),
                context=node["context"].strip(),
                creator=node["creator"],
                timestamp=node["timestamp"],
                tags=node.get("tags", []),
            )
            if result.duplicate:
                dupes += 1
            else:
                created += 1

        parts = [f"  {pool_name}: {created} created"]
        if dupes:
            parts.append(f"{dupes} skipped (duplicate)")
        print("".join(parts))

    print("\ndone.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--wipe", action="store_true", help="Delete registry/ before recreating.")
    parser.add_argument("--dry-run", action="store_true", help="Print plan without creating anything.")
    args = parser.parse_args()

    if args.wipe and not args.dry_run:
        wipe_registry()

    run(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
