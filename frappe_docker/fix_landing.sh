#!/bin/bash
APP_NAME="edu_theme"
JS_FILE="main-CeshOzD5.js"
CSS_FILE="main-uSrhrlA-.css"
WWW_DIR="apps/$APP_NAME/$APP_NAME/www"

# Re-write the file cleanly
cat > "$WWW_DIR/landing.html" <<EOF
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Education Portal</title>
<script>
 window.csrf_token = "{{ csrf_token }}";
</script>
<!-- Corrected Paths -->
<script type="module" src="/assets/$APP_NAME/frontend/assets/$JS_FILE"></script>
<link rel="stylesheet" href="/assets/$APP_NAME/frontend/assets/$CSS_FILE">
</head>
<body class="m-0 p-0 overflow-x-hidden">
<div id="app"></div>
</body>
</html>
EOF
 
echo ">>> landing.html has been reset with correct paths."

