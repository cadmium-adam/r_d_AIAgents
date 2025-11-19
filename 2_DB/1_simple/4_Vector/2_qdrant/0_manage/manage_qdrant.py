#!/usr/bin/env python3
"""
Qdrant API Management Script

This script helps manage a Qdrant instance running on Docker.
Features:
- List all collections
- View sample data from collections
- Collection statistics
"""

from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
import typer
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from typing import Optional
import json

app = typer.Typer(help="Qdrant Management Tool")
console = Console()

# Qdrant connection settings
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333


def get_qdrant_client():
    """Get Qdrant client connection"""
    try:
        client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        return client
    except Exception as e:
        console.print(f"[red]Error connecting to Qdrant: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def list_collections():
    """List all collections in Qdrant"""
    client = get_qdrant_client()

    try:
        collections = client.get_collections()

        if not collections.collections:
            console.print("[yellow]No collections found[/yellow]")
            return

        table = Table(title="Qdrant Collections")
        table.add_column("Name", style="cyan")
        table.add_column("Vector Count", style="green")
        table.add_column("Vector Size", style="magenta")
        table.add_column("Distance", style="blue")

        for collection in collections.collections:
            try:
                info = client.get_collection(collection.name)
                # Get actual count using collection info
                count = (
                    info.points_count
                    if hasattr(info, "points_count")
                    else (info.vectors_count or 0)
                )
                vector_size = (
                    info.config.params.vectors.size
                    if info.config.params.vectors
                    else "N/A"
                )
                distance = (
                    info.config.params.vectors.distance.value
                    if info.config.params.vectors
                    else "N/A"
                )
                table.add_row(
                    collection.name, str(count), str(vector_size), str(distance)
                )
            except Exception as e:
                table.add_row(collection.name, f"Error: {e}", "", "")

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error listing collections: {e}[/red]")


@app.command()
def show_collection(
    name: str = typer.Argument(..., help="Collection name"),
    limit: int = typer.Option(5, "--limit", "-l", help="Number of items to show"),
):
    """Show sample data from a specific collection"""
    client = get_qdrant_client()

    try:
        # Get collection info
        info = client.get_collection(name)
        console.print(f"[bold cyan]Collection: {name}[/bold cyan]")
        count = (
            info.points_count
            if hasattr(info, "points_count")
            else (info.vectors_count or 0)
        )
        console.print(f"Total vectors: {count}")

        if not count:
            console.print("[yellow]Collection is empty[/yellow]")
            return

        # Get sample data
        results = client.scroll(
            collection_name=name, limit=limit, with_payload=True, with_vectors=True
        )

        if not results[0]:
            console.print("[yellow]No data found[/yellow]")
            return

        # Display results
        for i, point in enumerate(results[0]):
            console.print(f"\n[bold green]Point {i+1}:[/bold green]")
            console.print(f"ID: {point.id}")

            if point.payload:
                console.print(f"Payload: {json.dumps(point.payload, indent=2)}")

            if point.vector:
                if isinstance(point.vector, list):
                    console.print(
                        f"Vector: [{len(point.vector)} dimensions] {point.vector[:5]}..."
                    )
                elif isinstance(point.vector, dict):
                    # Named vectors
                    for vector_name, vector_data in point.vector.items():
                        console.print(
                            f"Vector '{vector_name}': [{len(vector_data)} dimensions] {vector_data[:5]}..."
                        )

    except Exception as e:
        console.print(f"[red]Error accessing collection '{name}': {e}[/red]")


@app.command()
def collection_stats(name: str = typer.Argument(..., help="Collection name")):
    """Show detailed statistics for a collection"""
    client = get_qdrant_client()

    try:
        info = client.get_collection(name)

        console.print(f"[bold cyan]Collection Statistics: {name}[/bold cyan]")

        # Basic stats
        count = (
            info.points_count
            if hasattr(info, "points_count")
            else (info.vectors_count or 0)
        )
        console.print(f"Total vectors: {count}")

        if count == 0:
            console.print("[yellow]Collection is empty[/yellow]")
            return

        # Collection configuration
        config = info.config
        if config.params.vectors:
            console.print(f"Vector size: {config.params.vectors.size}")
            console.print(f"Distance metric: {config.params.vectors.distance.value}")

        # Get sample data to analyze payloads
        results = client.scroll(
            collection_name=name,
            limit=100,  # Sample more for better stats
            with_payload=True,
            with_vectors=False,
        )

        # Payload analysis
        if results[0]:
            payload_keys = set()
            for point in results[0]:
                if point.payload:
                    payload_keys.update(point.payload.keys())

            if payload_keys:
                console.print(f"Payload fields: {', '.join(sorted(payload_keys))}")

        # Storage info
        if hasattr(info, "status") and info.status:
            console.print(f"Status: {info.status}")

    except Exception as e:
        console.print(f"[red]Error getting stats for collection '{name}': {e}[/red]")


@app.command()
def create_collection(
    name: str = typer.Argument(..., help="Collection name to create"),
    vector_size: int = typer.Option(
        384, "--vector-size", "-s", help="Vector dimension size"
    ),
    distance: str = typer.Option(
        "Cosine", "--distance", "-d", help="Distance metric (Cosine, Euclidean, Dot)"
    ),
):
    """Create a new collection in Qdrant"""
    client = get_qdrant_client()

    try:
        # Check if collection already exists
        try:
            client.get_collection(name)
            console.print(f"[red]Collection '{name}' already exists[/red]")
            raise typer.Exit(1)
        except Exception:
            # Collection doesn't exist, which is what we want
            pass

        # Validate distance metric
        valid_distances = ["Cosine", "Euclidean", "Dot", "Manhattan"]
        if distance not in valid_distances:
            console.print(f"[red]Invalid distance metric: {distance}[/red]")
            console.print(f"Available options: {', '.join(valid_distances)}")
            raise typer.Exit(1)

        # Import required classes
        from qdrant_client.models import Distance, VectorParams

        # Map string to Distance enum
        distance_map = {
            "Cosine": Distance.COSINE,
            "Euclidean": Distance.EUCLID,
            "Dot": Distance.DOT,
            "Manhattan": Distance.MANHATTAN,
        }

        # Create collection
        client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(
                size=vector_size, distance=distance_map[distance]
            ),
        )

        console.print(f"[green]✓ Collection '{name}' created successfully[/green]")
        console.print(f"  Vector size: {vector_size}")
        console.print(f"  Distance metric: {distance}")

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Error creating collection '{name}': {e}[/red]")
        raise typer.Exit(1)


@app.command()
def remove_collection(
    name: str = typer.Argument(..., help="Collection name to remove"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt"),
):
    """Remove a collection from Qdrant"""
    client = get_qdrant_client()

    try:
        # Check if collection exists and get count
        try:
            info = client.get_collection(name)
            count = (
                info.points_count
                if hasattr(info, "points_count")
                else (info.vectors_count or 0)
            )
        except Exception:
            console.print(f"[red]Collection '{name}' not found[/red]")
            raise typer.Exit(1)

        # Confirmation prompt
        if not force:
            console.print(
                f"[yellow]Collection '{name}' contains {count} vectors[/yellow]"
            )
            confirm = typer.confirm("Are you sure you want to remove this collection?")
            if not confirm:
                console.print("[cyan]Operation cancelled[/cyan]")
                raise typer.Exit(0)

        # Remove the collection
        client.delete_collection(name)
        console.print(f"[green]✓ Collection '{name}' removed successfully[/green]")

    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Error removing collection '{name}': {e}[/red]")
        raise typer.Exit(1)


@app.command()
def health_check():
    """Check Qdrant connection and status"""
    try:
        client = get_qdrant_client()
        collections = client.get_collections()

        console.print("[green]✓ Qdrant connection successful[/green]")
        console.print(f"Server: {QDRANT_HOST}:{QDRANT_PORT}")
        console.print(f"Collections: {len(collections.collections)}")

        # Show cluster info if available
        try:
            cluster_info = client.get_cluster_info()
            console.print(f"Cluster status: {cluster_info.status}")
        except:
            pass

    except Exception as e:
        console.print(f"[red]✗ Qdrant connection failed: {e}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
