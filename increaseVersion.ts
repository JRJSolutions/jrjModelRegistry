#!/usr/bin/env bun

const fs = require("fs");
const path = require("path");

function incrementVersion(version) {
  let [major, minor, patch] = version.split(".").map(Number);
  patch += 1;
  if (patch >= 999) {
    patch = 0;
    minor += 1;
    if (minor >= 999) {
      minor = 0;
      major += 1;
    }
  }
  return `${major}.${minor}.${patch}`;
}

function updatePyprojectToml(newVersion) {
  const filePath = path.join(__dirname, "pyproject.toml");
  let content = fs.readFileSync(filePath, "utf8");

  const updatedContent = content.replace(
    /version\s*=\s*["'](\d+\.\d+\.\d+)["']/,
    `version = "${newVersion}"`
  );

  fs.writeFileSync(filePath, updatedContent, "utf8");
}

function updatePackageJson(newVersion) {
  const filePath = path.join(__dirname, "package.json");
  if (!fs.existsSync(filePath)) return;

  const packageJson = JSON.parse(fs.readFileSync(filePath, "utf8"));
  packageJson.version = newVersion;
  fs.writeFileSync(filePath, JSON.stringify(packageJson, null, 2), "utf8");
}

function main() {
  const pyprojectPath = path.join(__dirname, "pyproject.toml");
  if (!fs.existsSync(pyprojectPath)) {
    console.error("pyproject.toml not found.");
    process.exit(1);
  }

  const content = fs.readFileSync(pyprojectPath, "utf8");
  const match = content.match(/version\s*=\s*["'](\d+\.\d+\.\d+)["']/);
  if (!match) {
    console.error("Failed to find version in pyproject.toml");
    process.exit(1);
  }

  const currentVersion = match[1];
  const newVersion = incrementVersion(currentVersion);

  updatePyprojectToml(newVersion);
  updatePackageJson(newVersion);

  console.log(`✅ Version updated to ${newVersion}`);
}

main();
