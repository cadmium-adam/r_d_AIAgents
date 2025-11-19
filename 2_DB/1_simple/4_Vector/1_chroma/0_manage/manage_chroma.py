#!/usr/bin/env python3
"""
ChromaDB Management Script

This script helps manage a ChromaDB instance running on Docker.
Features:
- List all collections
- View sample data from collections
- Collection statistics
"""

import chromadb
from chromadb.config import Settings
import typer
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from typing import Optional
import json

app = typer.Typer(help="ChromaDB Management Tool")
console = Console()

# ChromaDB connection settings
CHROMA_HOST = "localhost"
CHROMA_PORT = 8100


def get_chroma_client():
    """Get ChromaDB client connection"""
    try:
        client = chromadb.HttpClient(
            host=CHROMA_HOST, port=CHROMA_PORT, settings=Settings(allow_reset=True)
        )
        return client
    except Exception as e:
        console.print(f"[red]Error connecting to ChromaDB: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def list_collections():
    """List all collections in ChromaDB"""
    client = get_chroma_client()

    try:
        collections = client.list_collections()

        if not collections:
            console.print("[yellow]No collections found[/yellow]")
            return

        table = Table(title="ChromaDB Collections")
        table.add_column("Name", style="cyan")
        table.add_column("ID", style="magenta")
        table.add_column("Count", style="green")

        for collection in collections:
            try:
                coll = client.get_collection(collection.name)
                count = coll.count()
                table.add_row(collection.name, str(collection.id), str(count))
            except Exception as e:
                table.add_row(collection.name, str(collection.id), f"Error: {e}")

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error listing collections: {e}[/red]")


@app.command()
def show_collection(
    name: str = typer.Argument(..., help="Collection name"),
    limit: int = typer.Option(5, "--limit", "-l", help="Number of items to show"),
):
    """Show sample data from a specific collection"""
    client = get_chroma_client()

    try:
        collection = client.get_collection(name)

        # Get collection info
        console.print(f"[bold cyan]Collection: {name}[/bold cyan]")
        console.print(f"Total items: {collection.count()}")

        if collection.count() == 0:
            console.print("[yellow]Collection is empty[/yellow]")
            return

        # Get sample data
        results = collection.get(
            limit=limit, include=["documents", "metadatas", "embeddings"]
        )

        if not results["ids"]:
            console.print("[yellow]No data found[/yellow]")
            return

        # Display results
        for i, doc_id in enumerate(results["ids"]):
            console.print(f"\n[bold green]Item {i+1}:[/bold green]")
            console.print(f"ID: {doc_id}")

            if results["documents"] and i < len(results["documents"]):
                doc = results["documents"][i]
                if doc:
                    # Truncate long documents
                    display_doc = doc[:200] + "..." if len(doc) > 200 else doc
                    console.print(f"Document: {display_doc}")

            if results["metadatas"] and i < len(results["metadatas"]):
                metadata = results["metadatas"][i]
                if metadata:
                    console.print(f"Metadata: {json.dumps(metadata, indent=2)}")

            if results["embeddings"] and i < len(results["embeddings"]):
                embedding = results["embeddings"][i]
                if embedding:
                    console.print(
                        f"Embedding: [{len(embedding)} dimensions] {embedding[:5]}..."
                    )

    except Exception as e:
        console.print(f"[red]Error accessing collection '{name}': {e}[/red]")


@app.command()
def collection_stats(name: str = typer.Argument(..., help="Collection name")):
    """Show detailed statistics for a collection"""
    client = get_chroma_client()

    try:
        collection = client.get_collection(name)

        console.print(f"[bold cyan]Collection Statistics: {name}[/bold cyan]")

        # Basic stats
        count = collection.count()
        console.print(f"Total documents: {count}")

        if count == 0:
            console.print("[yellow]Collection is empty[/yellow]")
            return

        # Get all data to analyze
        results = collection.get(include=["documents", "metadatas"])

        # Document length statistics
        if results["documents"]:
            doc_lengths = [len(doc) if doc else 0 for doc in results["documents"]]
            console.print(
                f"Document lengths - Min: {min(doc_lengths)}, Max: {max(doc_lengths)}, Avg: {sum(doc_lengths)/len(doc_lengths):.1f}"
            )

        # Metadata analysis
        if results["metadatas"]:
            metadata_keys = set()
            for metadata in results["metadatas"]:
                if metadata:
                    metadata_keys.update(metadata.keys())

            if metadata_keys:
                console.print(f"Metadata fields: {', '.join(sorted(metadata_keys))}")

    except Exception as e:
        console.print(f"[red]Error getting stats for collection '{name}': {e}[/red]")


@app.command()
def create_collection(
    name: str = typer.Argument(..., help="Collection name to create"),
    embedding_function: str = typer.Option("default", "--embedding", "-e", help="Embedding function (default, openai, sentence-transformers)"),
):
    """Create a new collection in ChromaDB"""
    client = get_chroma_client()
    
    try:
        # Check if collection already exists
        try:
            client.get_collection(name)
            console.print(f"[red]Collection '{name}' already exists[/red]")
            raise typer.Exit(1)
        except Exception:
            # Collection doesn't exist, which is what we want
            pass
        
        # Create collection with specified embedding function
        if embedding_function == "default":
            collection = client.create_collection(name=name)
        elif embedding_function == "openai":
            try:
                from chromadb.utils import embedding_functions
                openai_ef = embedding_functions.OpenAIEmbeddingFunction()
                collection = client.create_collection(name=name, embedding_function=openai_ef)
            except ImportError:
                console.print("[red]OpenAI embedding function not available. Install with: pip install openai[/red]")
                raise typer.Exit(1)
        elif embedding_function == "sentence-transformers":
            try:
                from chromadb.utils import embedding_functions
                sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
                collection = client.create_collection(name=name, embedding_function=sentence_transformer_ef)
            except ImportError:
                console.print("[red]SentenceTransformer embedding function not available. Install with: pip install sentence-transformers[/red]")
                raise typer.Exit(1)
        else:
            console.print(f"[red]Unknown embedding function: {embedding_function}[/red]")
            console.print("Available options: default, openai, sentence-transformers")
            raise typer.Exit(1)
        
        console.print(f"[green]✓ Collection '{name}' created successfully with {embedding_function} embedding function[/green]")
        
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
    """Remove a collection from ChromaDB"""
    client = get_chroma_client()
    
    try:
        # Check if collection exists
        try:
            collection = client.get_collection(name)
            count = collection.count()
        except Exception:
            console.print(f"[red]Collection '{name}' not found[/red]")
            raise typer.Exit(1)
        
        # Confirmation prompt
        if not force:
            console.print(f"[yellow]Collection '{name}' contains {count} items[/yellow]")
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
    """Check ChromaDB connection and status"""
    try:
        client = get_chroma_client()
        collections = client.list_collections()

        console.print("[green]✓ ChromaDB connection successful[/green]")
        console.print(f"Server: {CHROMA_HOST}:{CHROMA_PORT}")
        console.print(f"Collections: {len(collections)}")

        # Show version if available
        try:
            heartbeat = client.heartbeat()
            console.print(f"Heartbeat: {heartbeat}")
        except:
            pass

    except Exception as e:
        console.print(f"[red]✗ ChromaDB connection failed: {e}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
