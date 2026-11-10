from __future__ import annotations

import pathlib
import tempfile
import unittest

from prepare_content import (
    build_order_map,
    build_path_map,
    parse_summary,
    prepare_content,
    sanitize_asset_name,
    sanitize_md_rel_path,
    transform_markdown,
)


class PrepareContentTests(unittest.TestCase):
    def test_sanitize_names(self) -> None:
        self.assertEqual(sanitize_asset_name("image (1).png"), "image-1.png")
        self.assertEqual(sanitize_asset_name("image.png"), "image.png")
        self.assertEqual(sanitize_md_rel_path("README.md"), "index.md")
        self.assertEqual(sanitize_md_rel_path("web/README.md"), "web/index.md")
        self.assertEqual(
            sanitize_md_rel_path("crypto/ecc/ecdlp-+-crt.md"),
            "crypto/ecc/ecdlp-crt.md",
        )
        self.assertEqual(
            sanitize_md_rel_path("crypto/rsa/williams-p+1.md"),
            "crypto/rsa/williams-p-plus-1.md",
        )

    def test_fenced_code_blocks_are_untouched(self) -> None:
        raw = (
            "# SSTI\n\n"
            "{% embed url=\"https://example.com/ref\" %}\n\n"
            "```jinja2\n"
            "{% for c in ''.__class__.__mro__ %}{{ c }}{% endfor %}\n"
            "<figure><img src=\"../../.gitbook/assets/image (1).png\" alt=\"\"></figure>\n"
            "[RSA](rsa/README.md)\n"
            "```\n"
        )
        out = transform_markdown(
            raw_text=raw,
            src_rel="web/ssti.md",
            title_map={"web/ssti.md": "SSTI"},
            entries=[(0, "Web", "web/README.md"), (1, "SSTI", "web/ssti.md")],
            path_map={"web/README.md": "web/index.md", "web/ssti.md": "web/ssti.md"},
            asset_map={"image (1).png": "image-1.png"},
        )
        self.assertIn('title: "SSTI"', out)
        self.assertNotIn("\n# SSTI\n", out)
        self.assertIn("- [https://example.com/ref](https://example.com/ref)", out)
        # Code block contents must remain identical
        self.assertIn("{% for c in ''.__class__.__mro__ %}{{ c }}{% endfor %}", out)
        self.assertIn('[RSA](rsa/README.md)', out)

    def test_links_and_figures_rewritten_outside_code(self) -> None:
        raw = (
            "---\n"
            "description: 'Referensi: DawgCTF'\n"
            "---\n\n"
            "# Recover N\n\n"
            '<figure><img src="../../.gitbook/assets/image (1).png" alt="diag"><figcaption></figcaption></figure>\n\n'
            "See [RSA](../rsa/README.md) and [Williams](../rsa/williams-p+1.md#trick).\n"
        )
        path_map = {
            "crypto/lcg/recover-n.md": "crypto/lcg/recover-n.md",
            "crypto/rsa/README.md": "crypto/rsa/index.md",
            "crypto/rsa/williams-p+1.md": "crypto/rsa/williams-p-plus-1.md",
        }
        out = transform_markdown(
            raw_text=raw,
            src_rel="crypto/lcg/recover-n.md",
            title_map={"crypto/lcg/recover-n.md": "Recover N"},
            entries=[],
            path_map=path_map,
            asset_map={"image (1).png": "image-1.png"},
        )
        self.assertIn('description: "Referensi: DawgCTF"', out)
        self.assertIn('title: "Recover N"', out)
        self.assertIn("![diag](assets/image-1.png)", out)
        self.assertIn("[RSA](crypto/rsa/index.md)", out)
        self.assertIn("[Williams](crypto/rsa/williams-p-plus-1.md#trick)", out)

    def test_real_repository_preparation(self) -> None:
        repo_root = pathlib.Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = pathlib.Path(tmp) / "content"
            stats = prepare_content(repo_root=repo_root, output_dir=out_dir)
            self.assertGreaterEqual(stats["markdown_files"], 165)
            self.assertEqual(stats["assets"], 6)
            self.assertTrue((out_dir / "index.md").is_file())
            self.assertTrue((out_dir / "web" / "index.md").is_file())
            self.assertTrue((out_dir / "assets" / "image-1.png").is_file())


if __name__ == "__main__":
    unittest.main()
