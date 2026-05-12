#!/usr/bin/env node

const { spawn, execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');

const REPO_URL = 'https://github.com/anhdt19942020/craftpowers';
const INSTALL_DIR = path.join(os.homedir(), '.claude', 'plugins', 'man');
const CLAUDE_DIR = path.join(os.homedir(), '.claude');

const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  cyan: '\x1b[36m',
  bold: '\x1b[1m',
};

function log(msg) { console.log(msg); }
function ok(msg) { console.log(`${colors.green}✓${colors.reset} ${msg}`); }
function err(msg) { console.log(`${colors.red}✗${colors.reset} ${msg}`); }
function warn(msg) { console.log(`${colors.yellow}!${colors.reset} ${msg}`); }
function info(msg) { console.log(`${colors.cyan}→${colors.reset} ${msg}`); }

function run(cmd, opts = {}) {
  try {
    return execSync(cmd, { encoding: 'utf8', stdio: opts.silent ? 'pipe' : 'inherit', ...opts });
  } catch (e) {
    if (!opts.ignoreError) throw e;
    return null;
  }
}

function checkPython() {
  try {
    execSync('python --version', { stdio: 'pipe' });
    return 'python';
  } catch {
    try {
      execSync('python3 --version', { stdio: 'pipe' });
      return 'python3';
    } catch {
      return null;
    }
  }
}

function checkGit() {
  try {
    execSync('git --version', { stdio: 'pipe' });
    return true;
  } catch {
    return false;
  }
}

// Commands

function init() {
  log(`\n${colors.bold}mankit init${colors.reset} — Install mankit\n`);

  // Check prerequisites
  if (!checkGit()) {
    err('Git not found. Please install git first.');
    process.exit(1);
  }

  const python = checkPython();
  if (!python) {
    err('Python not found. Please install Python 3.8+ first.');
    process.exit(1);
  }

  // Create ~/.claude if needed
  if (!fs.existsSync(CLAUDE_DIR)) {
    fs.mkdirSync(CLAUDE_DIR, { recursive: true });
    ok('Created ~/.claude directory');
  }

  // Clone or update repo
  if (fs.existsSync(INSTALL_DIR)) {
    info('mankit already installed, updating...');
    run('git pull', { cwd: INSTALL_DIR });
    ok('Updated to latest version');
  } else {
    info(`Cloning mankit to ${INSTALL_DIR}...`);
    fs.mkdirSync(path.dirname(INSTALL_DIR), { recursive: true });
    run(`git clone ${REPO_URL} "${INSTALL_DIR}"`);
    ok('Cloned mankit repository');
  }

  // Run install script
  info('Running setup...');
  run(`${python} "${path.join(INSTALL_DIR, 'scripts', 'install.py')}"`);

  log(`\n${colors.green}${colors.bold}Done!${colors.reset} Restart Claude Code to activate mankit.\n`);
  log('Quick start:');
  log('  /man-check      — Verify installation');
  log('  /man-brainstorm — Start a new feature');
  log('  /man-fix        — Debug a bug');
  log('');
}

function update() {
  log(`\n${colors.bold}mankit update${colors.reset} — Update to latest\n`);

  if (!fs.existsSync(INSTALL_DIR)) {
    err('mankit not installed. Run: mankit init');
    process.exit(1);
  }

  const python = checkPython();
  if (!python) {
    err('Python not found.');
    process.exit(1);
  }

  info('Pulling latest changes...');
  run('git pull', { cwd: INSTALL_DIR });
  ok('Updated repository');

  info('Running setup...');
  run(`${python} "${path.join(INSTALL_DIR, 'scripts', 'install.py')}"`);

  log(`\n${colors.green}${colors.bold}Done!${colors.reset} Restart Claude Code to apply changes.\n`);
}

function doctor() {
  log(`\n${colors.bold}mankit doctor${colors.reset} — Health check\n`);

  let passed = 0;
  let failed = 0;

  // Check installation
  if (fs.existsSync(INSTALL_DIR)) {
    ok('mankit installed');
    passed++;
  } else {
    err('mankit not installed');
    failed++;
  }

  // Check Python
  const python = checkPython();
  if (python) {
    ok(`Python found (${python})`);
    passed++;
  } else {
    err('Python not found');
    failed++;
  }

  // Check Git
  if (checkGit()) {
    ok('Git found');
    passed++;
  } else {
    err('Git not found');
    failed++;
  }

  // Check settings.json
  const settingsPath = path.join(CLAUDE_DIR, 'settings.json');
  if (fs.existsSync(settingsPath)) {
    try {
      const settings = JSON.parse(fs.readFileSync(settingsPath, 'utf8'));
      if (settings.hooks) {
        ok('Hooks configured');
        passed++;
      } else {
        warn('Hooks not configured');
        failed++;
      }
    } catch {
      err('settings.json invalid');
      failed++;
    }
  } else {
    err('settings.json not found');
    failed++;
  }

  // Check symlinks
  const links = ['agents', 'skills', 'commands'];
  for (const link of links) {
    const linkPath = path.join(CLAUDE_DIR, link);
    if (fs.existsSync(linkPath)) {
      ok(`${link}/ linked`);
      passed++;
    } else {
      err(`${link}/ not linked`);
      failed++;
    }
  }

  log(`\n${passed} passed, ${failed} failed\n`);

  if (failed > 0) {
    log('Run `mankit init` to fix issues.');
  }
}

function uninstall() {
  log(`\n${colors.bold}mankit uninstall${colors.reset} — Remove mankit\n`);

  // Remove symlinks
  const links = ['agents', 'skills', 'commands'];
  for (const link of links) {
    const linkPath = path.join(CLAUDE_DIR, link);
    if (fs.existsSync(linkPath)) {
      try {
        fs.rmSync(linkPath, { recursive: true });
        ok(`Removed ${link}/`);
      } catch (e) {
        warn(`Could not remove ${link}/: ${e.message}`);
      }
    }
  }

  // Remove install directory
  if (fs.existsSync(INSTALL_DIR)) {
    try {
      fs.rmSync(INSTALL_DIR, { recursive: true });
      ok('Removed mankit directory');
    } catch (e) {
      warn(`Could not remove install directory: ${e.message}`);
    }
  }

  // Note: Don't remove settings.json hooks — user may have other hooks

  log(`\n${colors.green}${colors.bold}Done!${colors.reset} mankit removed.\n`);
  log('Note: Hooks in ~/.claude/settings.json were not removed.');
  log('Edit settings.json manually to remove hooks if needed.\n');
}

function help() {
  log(`
${colors.bold}mankit${colors.reset} — AI coding methodology for Claude Code

${colors.bold}Usage:${colors.reset}
  mankit <command>

${colors.bold}Commands:${colors.reset}
  init        Install mankit (clone + setup)
  update      Update to latest version
  doctor      Health check
  uninstall   Remove mankit

${colors.bold}Examples:${colors.reset}
  mankit init       # First-time install
  mankit update     # Update to latest
  mankit doctor     # Check if everything works

${colors.bold}After install:${colors.reset}
  /man-check        # Verify in Claude Code
  /man-brainstorm   # Start a feature
  /man-fix          # Debug a bug
  /man-plan         # Create implementation plan

${colors.bold}More info:${colors.reset}
  https://github.com/anhdt19942020/craftpowers
`);
}

// Main
const command = process.argv[2];

switch (command) {
  case 'init':
  case 'install':
  case 'new':
    init();
    break;
  case 'update':
  case 'upgrade':
    update();
    break;
  case 'doctor':
  case 'check':
    doctor();
    break;
  case 'uninstall':
  case 'remove':
    uninstall();
    break;
  case '--help':
  case '-h':
  case 'help':
  case undefined:
    help();
    break;
  default:
    err(`Unknown command: ${command}`);
    log('Run `mankit --help` for usage.');
    process.exit(1);
}
