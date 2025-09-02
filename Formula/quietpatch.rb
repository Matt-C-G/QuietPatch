# typed: false
# frozen_string_literal: true

class Quietpatch < Formula
  desc "Privacy-first vuln scanner with deterministic HTML reports"
  homepage "https://github.com/Matt-C-G/QuietPatch"
  version "0.2.5"  # auto-bumped by CI step below
  license "MIT"

  # Versioned, stable URL + sha256 (macOS arm64 build zip)
  url "https://github.com/Matt-C-G/QuietPatch/releases/download/v#{version}/quietpatch-#{version}-macos-arm64.zip"
  sha256 "<REPLACE_SHA256>"  # auto-bumped

  # Linuxbrew users can point this formula to the linux zip instead (optional split formula).
  depends_on "python@3.11"

  livecheck do
    url :stable
    strategy :github_latest
  end

  def install
    libexec.install Dir["*"]  # PEX + launchers + policies/catalog if present
    # Wrapper: keeps user's system clean and sets PEX_ROOT
    (bin/"quietpatch").write <<~SH
      #!/usr/bin/env bash
      set -euo pipefail
      export PEX_ROOT="${XDG_CACHE_HOME:-$HOME/.cache}/quietpatch/.pexroot"
      exec "#{Formula["python@3.11"].opt_bin}/python3.11" "#{libexec}/quietpatch-macos-arm64-py311.pex" "$@"
    SH
    chmod 0755, bin/"quietpatch"
  end

  test do
    system "#{bin}/quietpatch", "scan", "--help"
  end
end
