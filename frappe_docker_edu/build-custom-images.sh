#!/bin/bash
# Build Custom Frappe/ERPNext Images with edu_theme app
# Run this from your project root where docker-compose.yml exists

set -e  # Exit on any error

# Configuration
FRAPPE_VERSION="v15.0.0"
ERPNEXT_VERSION="v15.0.0"
REGISTRY="docker.io"  # Change to your registry if needed
IMAGE_PREFIX="zubbystudio"  # Change to your Docker Hub username or registry prefix

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Building Custom Frappe/ERPNext Images with edu_theme...${NC}"

# Verify edu_theme app exists
if [ ! -d "./apps/edu_theme" ]; then
    echo -e "${RED}Error: ./apps/edu_theme directory not found${NC}"
    echo "Please ensure edu_theme app is in ./apps/edu_theme"
    exit 1
fi

# Verify Dockerfiles exist
if [ ! -f "Dockerfile.custom-backend" ] || [ ! -f "Dockerfile.custom-nginx" ]; then
    echo -e "${RED}Error: Dockerfiles not found${NC}"
    echo "Please create Dockerfile.custom-backend and Dockerfile.custom-nginx"
    exit 1
fi

# Build Backend Image
echo -e "${YELLOW}Building custom backend image...${NC}"
docker build \
    --build-arg FRAPPE_VERSION=${FRAPPE_VERSION} \
    --build-arg ERPNEXT_VERSION=${ERPNEXT_VERSION} \
    -t ${REGISTRY}/${IMAGE_PREFIX}/erpnext:${ERPNEXT_VERSION}-edu_theme \
    -f Dockerfile.custom-backend \
    .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Backend image built successfully${NC}"
else
    echo -e "${RED}✗ Backend image build failed${NC}"
    exit 1
fi

# Build Nginx Image
echo -e "${YELLOW}Building custom nginx image...${NC}"
docker build \
    --build-arg ERPNEXT_VERSION=${ERPNEXT_VERSION} \
    -t ${REGISTRY}/${IMAGE_PREFIX}/erpnext-nginx:${ERPNEXT_VERSION}-edu_theme \
    -f Dockerfile.custom-nginx \
    .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Nginx image built successfully${NC}"
else
    echo -e "${RED}✗ Nginx image build failed${NC}"
    exit 1
fi

# Display built images
echo -e "${GREEN}Build complete! Images created:${NC}"
docker images | grep "${IMAGE_PREFIX}" | grep "edu_theme"

# Optional: Push to registry
read -p "Push images to registry? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Pushing backend image...${NC}"
    docker push ${REGISTRY}/${IMAGE_PREFIX}/erpnext:${ERPNEXT_VERSION}-edu_theme
    
    echo -e "${YELLOW}Pushing nginx image...${NC}"
    docker push ${REGISTRY}/${IMAGE_PREFIX}/erpnext-nginx:${ERPNEXT_VERSION}-edu_theme
    
    echo -e "${GREEN}✓ Images pushed to registry${NC}"
fi

echo -e "${GREEN}Done! Update your docker-compose.yml to use these images:${NC}"
echo "  backend:"
echo "    image: ${REGISTRY}/${IMAGE_PREFIX}/erpnext:${ERPNEXT_VERSION}-edu_theme"
echo "  frontend:"
echo "    image: ${REGISTRY}/${IMAGE_PREFIX}/erpnext-nginx:${ERPNEXT_VERSION}-edu_theme"
