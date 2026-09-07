"""Phase 9-2 Experiment/Multi-Governance Research Platform Core.

A research layer above the existing Phase 1-9 Components (Main, Judge,
Guard, Main Governance, RAG, Repair, Recording): this module never
reimplements their internal contracts, never becomes a central runtime
those Components depend on, and never hard-codes a Model/Provider/GD
identity into its own Domain types (see `domain/identity.py`). Callers
reach existing Components exclusively through this module's own
`ports.py` Actor Protocols, implemented by thin Adapters under
`adapters/experiment/`.
"""

from __future__ import annotations
