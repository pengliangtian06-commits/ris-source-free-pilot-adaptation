"""Small deterministic consistency gate for the explicit RIS cascade."""

from __future__ import annotations

import numpy as np

from ris_cascaded_generator_smoke import cascaded_hop, make_cascaded_channel


def main() -> None:
    ue_hop = np.array([1.0 + 2.0j, -0.5 + 0.25j, 0.75 - 1.0j])
    reflection = np.exp(1j * np.array([0.2, -0.4, 0.7]))
    bs_hop = np.array(
        [
            [0.2 + 0.1j, -0.3 + 0.5j],
            [0.4 - 0.2j, 0.1 + 0.6j],
            [-0.7 + 0.3j, 0.8 - 0.1j],
        ]
    )
    expected = ue_hop.T @ np.diag(reflection) @ bs_hop
    np.testing.assert_allclose(cascaded_hop(ue_hop, reflection, bs_hop), expected)

    rng = np.random.default_rng(20261003)
    channel = make_cascaded_channel(
        rng, n_subcarriers=16, n_tx=4, n_ris=16, beam_squint=True
    )
    if channel.shape != (16, 4) or not np.isfinite(channel).all():
        raise AssertionError(f"unexpected generator output: {channel.shape}")
    print("RIS cascade consistency test passed")


if __name__ == "__main__":
    main()
