"""Create a credential-scanned v1.0.3 reproducibility and submission bundle."""

from __future__ import annotations

import hashlib
import json
import os
import re
import zipfile
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RELEASE_VERSION = os.environ.get("RELEASE_VERSION", "v1.0.3")
PACKAGE = ROOT / f"submission_package_{RELEASE_VERSION}.zip"
MANIFEST = ROOT / f"submission_package_manifest_{RELEASE_VERSION}.json"

ALLOWLIST = [
    "README.md",
    "LICENSE",
    "LICENSE-CC-BY-4.0.txt",
    "PUBLIC_RELEASE_NOTES_v1.0.0.md",
    "PUBLIC_RELEASE_NOTES_v1.0.2.md",
    "PUBLIC_RELEASE_NOTES_v1.0.3.md",
    "AUTHORS.md",
    "CITATION.cff",
    "paper-draft-r025.tex",
    "references.bib",
    "REPRODUCTION_README_v1.0.3.md",
    "DATA_SOURCES.md",
    "Physical Communication投稿计划_v1.0.3.md",
    "Physical Communication投稿门槛核验_v1.0.3.md",
    "submission_checklist_physical_communication_v1.0.3.md",
    "nature_workflow_audit_R032.md",
    "nature_workflow_audit_R033.md",
    "claim_evidence_map_R032.md",
    "claim_evidence_map_R033.md",
    "supplementary_materials_R032.md",
    "supplementary_materials_R033.md",
    "supplementary_tables_r032.tex",
    "paper-tables/table_r014_shift_sweep.tex",
    "paper-tables/table_r017_capacity.tex",
    "paper-tables/table_r017_paired.tex",
    "paper-tables/table_r020_robustness.tex",
    "paper-tables/table_r021_physics_control.tex",
    "paper-tables/table_r024_cost.tex",
    "paper-tables/table_r032_omp.tex",
    "paper-tables/table_related_work.tex",
    "experiments/ris_cascaded_generator_smoke.py",
    "experiments/ris_cascaded_generator_consistency_test.py",
    "experiments/ris_explicit_omp_baseline.py",
    "experiments/ris_data_consistency_adapter_smoke.py",
    "experiments/ris_physics_consistent_adapter_smoke.py",
    "experiments/ris_sparse_omp_smoke.py",
    "experiments/ris_ofdm_baseline_smoke.py",
    "experiments/cloud_ris_adapter_lightning.py",
    "experiments/cloud_ris_shift_sweep_cpu.py",
    "experiments/aggregate_shift_sweep.py",
    "experiments/aggregate_cpu_artifacts.py",
    "experiments/cloud_ris_heldout_geometry_cpu.py",
    "experiments/cloud_ris_robustness_adapter_cpu.py",
    "experiments/cloud_ris_physics_preregistered_cpu.py",
    "experiments/cloud_ris_physics_ablation_cpu.py",
    "experiments/cloud_ris_full_model_heldout_cpu.py",
    "experiments/benchmark_adaptation_cost.py",
    "experiments/export_latex_tables.py",
    "experiments/create_submission_package.py",
    "experiments/export_model_weights.py",
    "experiments/verify_model_weights.py",
    "experiments/plot_paper_figures.py",
    "experiments/related_work_matrix.json",
    "refine-logs/FINAL_NOVELTY_PASS_20261002.json",
    "experiments/ris_cascaded_generator_smoke_results.json",
    "experiments/cloud_ris_adapter_lightning_smoke_seed20261002_results.json",
    "experiments/cloud_ris_shift_sweep_full_seed20261002.json",
    "experiments/cloud_ris_shift_sweep_full_seed20261003.json",
    "experiments/cloud_ris_shift_sweep_full_seed20261004.json",
    "experiments/cloud_ris_shift_sweep_full_3seed_summary.json",
    "experiments/cloud_ris_heldout_geometry_full_seed20261002.json",
    "experiments/cloud_ris_heldout_geometry_full_seed20261003.json",
    "experiments/cloud_ris_heldout_geometry_full_seed20261004.json",
    "experiments/cloud_ris_robustness_adapter_cpu_seed20261002.json",
    "experiments/cloud_ris_robustness_adapter_cpu_seed20261003.json",
    "experiments/cloud_ris_robustness_adapter_cpu_seed20261004.json",
    "experiments/cloud_ris_robustness_adapter_cpu_3seed_summary.json",
    "experiments/cloud_ris_physics_preregistered_cpu_seed20261002.json",
    "experiments/cloud_ris_physics_preregistered_cpu_seed20261003.json",
    "experiments/cloud_ris_physics_preregistered_cpu_seed20261004.json",
    "experiments/cloud_ris_physics_preregistered_cpu_3seed_summary.json",
    "experiments/cloud_ris_physics_ablation_seed20261002.json",
    "experiments/cloud_ris_full_model_heldout_seed20261002.json",
    "experiments/cloud_ris_full_model_heldout_seed20261003.json",
    "experiments/cloud_ris_full_model_heldout_seed20261004.json",
    "experiments/adaptation_cost_cpu_seed20261002.json",
    "experiments/ris_explicit_omp_baseline_results.json",
    "experiments/ris_ofdm_baseline_smoke_results.json",
    "experiments/ris_sparse_omp_smoke_results.json",
    "experiments/ris_data_consistency_adapter_smoke_results.json",
    "experiments/ris_physics_consistent_adapter_smoke_results.json",
    "requirements-cloud.txt",
    "figures/fig1_protocol.pdf",
    "figures/fig1_protocol.svg",
    "figures/fig1_protocol.tiff",
    "figures/fig1_protocol.alignment.json",
    "figures/fig1_protocol.collision.json",
    "figures/fig2_shift_sweep.pdf",
    "figures/fig2_shift_sweep.svg",
    "figures/fig2_shift_sweep.tiff",
    "figures/fig2_shift_sweep.alignment.json",
    "figures/fig2_shift_sweep.collision.json",
    "figures/fig3_classical_sensitivity.pdf",
    "figures/fig3_classical_sensitivity.svg",
    "figures/fig3_classical_sensitivity.tiff",
    "figures/fig3_classical_sensitivity.alignment.json",
    "figures/fig3_classical_sensitivity.collision.json",
    "figures/fig4_capacity_cost.pdf",
    "figures/fig4_capacity_cost.svg",
    "figures/fig4_capacity_cost.tiff",
    "figures/fig4_capacity_cost.alignment.json",
    "figures/fig4_capacity_cost.collision.json",
    "figures/fig5_robustness.pdf",
    "figures/fig5_robustness.svg",
    "figures/fig5_robustness.tiff",
    "figures/fig5_robustness.alignment.json",
    "figures/fig5_robustness.collision.json",
    "submission_declarations_v1.0.3.md",
    "cover_letter_physical_communication_v1.0.3.md",
    "highlights_physical_communication_v1.0.3.md",
    "graphical_abstract_brief_v1.0.3.md",
    "figures/graphical_abstract_v1.0.3.py",
    "figures/graphical_abstract_v1.0.3.pdf",
    "figures/graphical_abstract_v1.0.3.svg",
    "figures/graphical_abstract_v1.0.3.png",
    "figures/graphical_abstract_v1.0.3.tiff",
    "figures/graphical_abstract_v1.0.3.collision.json",
    "figures/graphical_abstract_v1.0.3.alignment.json",
    "weights/v1.0.3/weights_manifest.json",
    "weights/v1.0.3/source_estimator_seed20261002.pt",
    "weights/v1.0.3/source_estimator_seed20261003.pt",
    "weights/v1.0.3/source_estimator_seed20261004.pt",
    "weights/v1.0.3/adapter_seed20261002_angle0p04_delay1p2.pt",
    "weights/v1.0.3/adapter_seed20261002_angle0p08_delay1p4.pt",
    "weights/v1.0.3/adapter_seed20261002_angle0p12_delay1p6.pt",
    "weights/v1.0.3/adapter_seed20261002_angle0p18_delay2.pt",
    "weights/v1.0.3/adapter_seed20261003_angle0p04_delay1p2.pt",
    "weights/v1.0.3/adapter_seed20261003_angle0p08_delay1p4.pt",
    "weights/v1.0.3/adapter_seed20261003_angle0p12_delay1p6.pt",
    "weights/v1.0.3/adapter_seed20261003_angle0p18_delay2.pt",
    "weights/v1.0.3/adapter_seed20261004_angle0p04_delay1p2.pt",
    "weights/v1.0.3/adapter_seed20261004_angle0p08_delay1p4.pt",
    "weights/v1.0.3/adapter_seed20261004_angle0p12_delay1p6.pt",
    "weights/v1.0.3/adapter_seed20261004_angle0p18_delay2.pt",
]

SECRET_PATTERNS = [
    re.compile(r"\b(?:password|passwd|pwd)\s*[:=]\s*\S+", re.IGNORECASE),
    re.compile(
        r"\b(?:10|192\.168|172\.(?:1[6-9]|2\d|3[01]))(?:\.\d{1,3}){2,3}\b",
        re.IGNORECASE,
    ),
    re.compile(r"(?:C:|D:)[\\/]Users[\\/][^\s<>]+", re.IGNORECASE),
    re.compile(r"(?:ssh|scp)\s+[^\s]+@[^\s]+", re.IGNORECASE),
]


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def scan(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return []
    return [pattern.pattern for pattern in SECRET_PATTERNS if pattern.search(text)]


def main() -> None:
    entries: list[dict[str, object]] = []
    missing: list[str] = []
    violations: list[dict[str, object]] = []
    for relative_name in ALLOWLIST:
        path = ROOT / relative_name
        if not path.exists():
            missing.append(relative_name)
            continue
        found = scan(path)
        if found:
            violations.append({"path": relative_name, "patterns": found})
        entries.append({"path": relative_name, "bytes": path.stat().st_size, "sha256": digest(path)})
    if missing or violations:
        raise SystemExit(json.dumps({"missing": missing, "credential_violations": violations}, indent=2))

    manifest = {
        "schema": "submission-package/1.0",
        "generated_on": date.today().isoformat(),
        "package": PACKAGE.name,
        "allowlisted_files": entries,
        "excluded_by_design": [
            "private credentials and host details",
            "raw CUDA logs and stale CUDA artifacts not regenerated in the local CPU environment",
            "temporary LaTeX build products",
            "institution-authenticated JCR/CAS screenshots not supplied as authoritative records",
            "full-model weights that depend on a target support block",
        ],
        "credential_scan": {"passed": True, "patterns_checked": len(SECRET_PATTERNS)},
        "external_fields_remaining": [
            "institutional JCR/MJL and CAS evidence for the selected venue",
            "live Physical Communication submission-system fields and APC decision",
            "Zenodo version DOI for v1.0.3 until the tagged release is archived",
        ],
        "local_device_summary": {
            "canonical_shift": "cpu",
            "capacity": "cpu",
            "adaptation_cost": "cpu",
            "model_weights": "cpu_state_dict",
            "cuda_available_for_r032_rerun": False,
        },
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with zipfile.ZipFile(PACKAGE, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for item in entries:
            path = ROOT / str(item["path"])
            archive.write(path, arcname=str(item["path"]))
        archive.write(MANIFEST, arcname=MANIFEST.name)
    print(json.dumps({"package": str(PACKAGE), "files": len(entries), "credential_scan_passed": True}))


if __name__ == "__main__":
    main()
