# multi-pool-repo-example

Demo registry for [AlpheusCEF](https://github.com/AlpheusCEF) — a household
asset tracking example with three pools: vehicles, appliances, and remodeling.

Used for human testing, early feedback, and validating the alph CLI as the
engine evolves.

## Setup

```bash
# Install alph-cli first
pip install -e /path/to/alph-cli

# Create the registry from seed data
python seed.py

# Wipe and recreate from scratch
python seed.py --wipe

# Preview without creating anything
python seed.py --dry-run
```

## Registry structure

```
registry/
  config.yaml           # registry + pool declarations
  vehicles/             # pool: maintenance logs, purchase/sale records
    snapshots/          # fixed nodes (past events)
    pointers/           # live nodes (open items)
    .alph/
  appliances/           # pool: purchase dates, repairs, replacements
    ...
  remodeling/           # pool: projects, contractors, costs
    ...
```

## Kicking the tires

```bash
POOL=registry/vehicles
alph list --pool $POOL
alph show <node-id> --pool $POOL
alph add --pool $POOL -c "Oil change at 72,000 miles" --creator you@example.com
alph validate --pool $POOL
```

## Seed data

`seed.yaml` is the authoritative source. It contains the registry definition,
pool configs, and 27 mock nodes across a realistic household timeline (2019-2024).
The `registry/` directory is gitignored — always recreatable from `seed.yaml`.
