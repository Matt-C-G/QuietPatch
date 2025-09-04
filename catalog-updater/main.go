package main

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"time"
)

type Manifest struct {
	Catalog struct {
		Epoch         int    `json:"epoch"`
		SnapshotDate  string `json:"snapshot_date"`
		Latest        string `json:"latest"`
		SignatureExt  string `json:"signature_ext"`
		MinClient     string `json:"min_client"`
	} `json:"catalog"`
}

func must(err error) {
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}
}

func download(url, path string) {
	fmt.Printf("📥 Downloading %s -> %s\n", url, path)
	
	resp, err := http.Get(url)
	must(err)
	defer resp.Body.Close()
	
	file, err := os.Create(path)
	must(err)
	defer file.Close()
	
	_, err = io.Copy(file, resp.Body)
	must(err)
}

func main() {
	qp := filepath.Join(os.UserHomeDir(), ".quietpatch")
	db := filepath.Join(qp, "db")
	os.MkdirAll(db, 0o755)

	// Download manifest
	manifestURL := os.Getenv("QP_MANIFEST_URL")
	if manifestURL == "" {
		manifestURL = "https://raw.githubusercontent.com/Matt-C-G/QuietPatch/main/manifest.json"
	}
	
	resp, err := http.Get(manifestURL)
	must(err)
	defer resp.Body.Close()
	
	body, err := io.ReadAll(resp.Body)
	must(err)
	
	var m Manifest
	json.Unmarshal(body, &m)

	// Download manifest signature and verify
	manifestPath := filepath.Join(db, "manifest.json")
	manifestSigPath := filepath.Join(db, "manifest.json.minisig")
	
	download(manifestURL, manifestPath)
	download(manifestURL+".minisig", manifestSigPath)
	
	// Verify manifest signature
	cmd := exec.Command("minisign", "-Vm", manifestPath, "-P", os.Getenv("QP_MINISIGN_PUBKEY"))
	if err := cmd.Run(); err != nil {
		fmt.Fprintf(os.Stderr, "❌ Manifest signature verification failed: %v\n", err)
		os.Exit(1)
	}

	// Download database and signature
	zstPath := filepath.Join(db, "qp_db-latest.tar.zst")
	sigPath := zstPath + m.Catalog.SignatureExt
	
	download(m.Catalog.Latest, zstPath)
	download(m.Catalog.Latest+m.Catalog.SignatureExt, sigPath)

	// Verify database signature
	cmd = exec.Command("minisign", "-Vm", zstPath, "-P", os.Getenv("QP_MINISIGN_PUBKEY"))
	if err := cmd.Run(); err != nil {
		fmt.Fprintf(os.Stderr, "❌ Database signature verification failed: %v\n", err)
		os.Exit(1)
	}

	// Extract using quietpatch db apply
	cmd = exec.Command("quietpatch", "db", "apply", zstPath, sigPath)
	cmd.Env = append(os.Environ(), "QP_OFFLINE=1")
	if err := cmd.Run(); err != nil {
		fmt.Fprintf(os.Stderr, "❌ Database extraction failed: %v\n", err)
		os.Exit(1)
	}

	fmt.Printf("✅ Catalog updated successfully!\n")
	fmt.Printf("   Epoch: %d\n", m.Catalog.Epoch)
	fmt.Printf("   Date: %s\n", m.Catalog.SnapshotDate)
	fmt.Printf("   Location: %s\n", db)
}
