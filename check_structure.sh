#!/bin/bash
# Quick structure validation script

echo "🔍 Validating Project Structure..."
echo ""

errors=0

# Check directories exist
for dir in src src/api src/jdownloader src/verification src/utils scripts docs; do
    if [ -d "$dir" ]; then
        echo "✅ $dir/"
    else
        echo "❌ $dir/ (missing)"
        ((errors++))
    fi
done

echo ""

# Check key files exist
for file in main.py src/main.py src/api/api.py src/jdownloader/jd_auth_config.py; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file (missing)"
        ((errors++))
    fi
done

echo ""

if [ $errors -eq 0 ]; then
    echo "✅ All structure checks passed!"
    exit 0
else
    echo "❌ Found $errors issues"
    exit 1
fi
