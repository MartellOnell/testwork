#!/bin/bash

# Quick start script for task management service

echo "=== Task Management Service Quick Start ==="
echo ""

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "1. Building and starting services..."
docker-compose up -d --build

echo ""
echo "2. Waiting for services to be ready..."
sleep 10

echo ""
echo "3. Checking service health..."
docker-compose ps

echo ""
echo "=== Service is ready! ==="
echo ""
echo "API Documentation: http://localhost:8000/api/v1/docs"
echo "API Base URL: http://localhost:8000"
echo "RabbitMQ Management: http://localhost:15672 (guest/guest)"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f api"
echo "  docker-compose logs -f worker"
echo ""
echo "To stop services:"
echo "  docker-compose down"
echo ""
