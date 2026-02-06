#!/bin/bash

# ========================================
# InvestLens Privacy Data Cleanup Script
# ========================================
# 
# This script will permanently delete:
# - Backend data source configurations
# - API keys and endpoints stored in backend
# 
# Note: Frontend localStorage data must be 
# cleared manually through browser settings
# or the Settings page in the application.
# 
# ========================================

echo ""
echo "========================================"
echo " InvestLens Privacy Data Cleanup"
echo "========================================"
echo ""
echo "WARNING: This will PERMANENTLY DELETE:"
echo "  - Backend data source configurations"
echo "  - API endpoint settings"
echo ""
echo "Frontend data (API keys, settings) stored"
echo "in your browser must be cleared separately"
echo "through the Settings page or browser."
echo ""
echo "========================================"
echo ""

read -p "Do you want to continue? (y/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Cleanup cancelled. No files were deleted."
    echo ""
    exit 0
fi

echo ""
echo "Starting cleanup..."
echo ""

# Check if config directory exists
if [ -d "investlens-kernel/config" ]; then
    echo "[1/2] Checking backend config directory..."
    
    # Delete sources.json if it exists
    if [ -f "investlens-kernel/config/sources.json" ]; then
        rm -f "investlens-kernel/config/sources.json"
        echo "  ✓ Deleted: config/sources.json"
    else
        echo "  ℹ No sources.json found"
    fi
    
    # Delete .env if it exists (optional - uncomment if needed)
    # if [ -f "investlens-kernel/.env" ]; then
    #     rm -f "investlens-kernel/.env"
    #     echo "  ✓ Deleted: .env"
    # else
    #     echo "  ℹ No .env found"
    # fi
else
    echo "[1/2] No backend config directory found"
fi

echo ""
echo "[2/2] Backend cleanup complete!"
echo ""
echo "========================================"
echo " IMPORTANT: Next Steps"
echo "========================================"
echo ""
echo "To clear frontend data (API keys, settings):"
echo "  1. Option A: Use the \"Clear All Privacy Data\""
echo "     button in the Settings page"
echo "  2. Option B: Clear browser localStorage:"
echo "     - Chrome: F12 > Application > Local Storage"
echo "     - Firefox: F12 > Storage > Local Storage"
echo "     - Edge: F12 > Application > Local Storage"
echo ""
echo "========================================"
echo ""
