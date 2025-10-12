#!/usr/bin/env python3
"""Gelişmiş veri analizi ve görselleştirme."""

import argparse
import json
from pathlib import Path
from typing import Dict, List, Any

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import numpy as np
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def load_data(file_path: str) -> pd.DataFrame:
    """Load data from CSV or JSON file."""
    path = Path(file_path)
    
    if path.suffix == '.json':
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return pd.DataFrame(data)
    else:
        return pd.read_csv(file_path)

def clean_price_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and convert price data."""
    if 'price' in df.columns:
        # Remove currency symbols and convert to float
        df['price_clean'] = df['price'].str.replace(r'[^\d.,]', '', regex=True)
        df['price_clean'] = df['price_clean'].str.replace(',', '.')
        df['price_clean'] = pd.to_numeric(df['price_clean'], errors='coerce')
    
    return df

def analyze_pricing(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze pricing patterns."""
    if 'price_clean' not in df.columns:
        return {}
    
    price_stats = df['price_clean'].describe()
    
    # Price ranges
    price_ranges = {
        'Under $10': len(df[df['price_clean'] < 10]),
        '$10-$25': len(df[(df['price_clean'] >= 10) & (df['price_clean'] < 25)]),
        '$25-$50': len(df[(df['price_clean'] >= 25) & (df['price_clean'] < 50)]),
        '$50-$100': len(df[(df['price_clean'] >= 50) & (df['price_clean'] < 100)]),
        'Over $100': len(df[df['price_clean'] >= 100]),
    }
    
    return {
        'stats': price_stats.to_dict(),
        'ranges': price_ranges,
        'median': df['price_clean'].median(),
        'mean': df['price_clean'].mean(),
    }

def analyze_titles(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze product titles for common words and patterns."""
    if 'title' not in df.columns:
        return {}
    
    # Combine all titles
    all_titles = ' '.join(df['title'].fillna('').astype(str))
    
    # Common words analysis
    words = all_titles.lower().split()
    word_freq = pd.Series(words).value_counts().head(20)
    
    # Title length analysis
    title_lengths = df['title'].str.len()
    
    return {
        'word_frequency': word_freq.to_dict(),
        'avg_title_length': title_lengths.mean(),
        'title_length_stats': title_lengths.describe().to_dict(),
    }

def create_visualizations(df: pd.DataFrame, output_dir: str) -> None:
    """Create comprehensive visualizations."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Set style
    plt.style.use('seaborn-v0_8')
    sns.set_palette("husl")
    
    # 1. Price distribution
    if 'price_clean' in df.columns:
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Price histogram
        axes[0, 0].hist(df['price_clean'].dropna(), bins=30, alpha=0.7)
        axes[0, 0].set_title('Price Distribution')
        axes[0, 0].set_xlabel('Price ($)')
        axes[0, 0].set_ylabel('Frequency')
        
        # Price box plot
        axes[0, 1].boxplot(df['price_clean'].dropna())
        axes[0, 1].set_title('Price Box Plot')
        axes[0, 1].set_ylabel('Price ($)')
        
        # Price vs Rating (if available)
        if 'rating' in df.columns:
            df_clean = df.dropna(subset=['price_clean', 'rating'])
            if not df_clean.empty:
                axes[1, 0].scatter(df_clean['price_clean'], df_clean['rating'], alpha=0.6)
                axes[1, 0].set_title('Price vs Rating')
                axes[1, 0].set_xlabel('Price ($)')
                axes[1, 0].set_ylabel('Rating')
        
        # Top sellers by product count
        if 'seller' in df.columns:
            top_sellers = df['seller'].value_counts().head(10)
            axes[1, 1].bar(range(len(top_sellers)), top_sellers.values)
            axes[1, 1].set_title('Top Sellers by Product Count')
            axes[1, 1].set_xlabel('Seller Rank')
            axes[1, 1].set_ylabel('Product Count')
            axes[1, 1].set_xticks(range(len(top_sellers)))
            axes[1, 1].set_xticklabels(top_sellers.index, rotation=45, ha='right')
        
        plt.tight_layout()
        plt.savefig(output_path / 'price_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    # 2. Word cloud from titles
    if 'title' in df.columns:
        all_titles = ' '.join(df['title'].fillna('').astype(str))
        if all_titles.strip():
            wordcloud = WordCloud(
                width=800, height=400, 
                background_color='white',
                max_words=100,
                colormap='viridis'
            ).generate(all_titles)
            
            plt.figure(figsize=(10, 5))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            plt.title('Most Common Words in Product Titles', fontsize=16)
            plt.tight_layout()
            plt.savefig(output_path / 'wordcloud.png', dpi=300, bbox_inches='tight')
            plt.close()
    
    # 3. Seller analysis
    if 'seller' in df.columns:
        seller_stats = df.groupby('seller').agg({
            'price_clean': ['count', 'mean', 'median'] if 'price_clean' in df.columns else 'count',
            'title': 'count'
        }).round(2)
        
        # Flatten column names
        seller_stats.columns = ['_'.join(col).strip() for col in seller_stats.columns]
        seller_stats = seller_stats.sort_values('title_count', ascending=False).head(20)
        
        fig, ax = plt.subplots(figsize=(12, 8))
        seller_stats['title_count'].plot(kind='bar', ax=ax)
        ax.set_title('Top 20 Sellers by Product Count')
        ax.set_xlabel('Seller')
        ax.set_ylabel('Product Count')
        ax.tick_params(axis='x', rotation=45)
        plt.tight_layout()
        plt.savefig(output_path / 'seller_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()

def generate_report(df: pd.DataFrame, output_dir: str) -> str:
    """Generate comprehensive analysis report."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    report_lines = [
        "# Etsy Scraped Data Analysis Report",
        "",
        f"**Total Products:** {len(df)}",
        f"**Analysis Date:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Data Overview",
        "",
    ]
    
    # Basic stats
    report_lines.append(f"- **Columns:** {', '.join(df.columns.tolist())}")
    report_lines.append(f"- **Missing Data:** {df.isnull().sum().sum()} cells")
    report_lines.append("")
    
    # Price analysis
    if 'price_clean' in df.columns:
        price_analysis = analyze_pricing(df)
        report_lines.extend([
            "## Price Analysis",
            "",
            f"- **Average Price:** ${price_analysis.get('mean', 0):.2f}",
            f"- **Median Price:** ${price_analysis.get('median', 0):.2f}",
            "",
            "### Price Ranges:",
        ])
        
        for range_name, count in price_analysis.get('ranges', {}).items():
            percentage = (count / len(df)) * 100
            report_lines.append(f"- **{range_name}:** {count} products ({percentage:.1f}%)")
        report_lines.append("")
    
    # Title analysis
    if 'title' in df.columns:
        title_analysis = analyze_titles(df)
        report_lines.extend([
            "## Title Analysis",
            "",
            f"- **Average Title Length:** {title_analysis.get('avg_title_length', 0):.1f} characters",
            "",
            "### Most Common Words:",
        ])
        
        for word, freq in list(title_analysis.get('word_frequency', {}).items())[:10]:
            report_lines.append(f"- **{word}:** {freq} times")
        report_lines.append("")
    
    # Seller analysis
    if 'seller' in df.columns:
        top_sellers = df['seller'].value_counts().head(10)
        report_lines.extend([
            "## Top Sellers",
            "",
        ])
        
        for i, (seller, count) in enumerate(top_sellers.items(), 1):
            report_lines.append(f"{i}. **{seller}:** {count} products")
        report_lines.append("")
    
    # Save report
    report_content = "\n".join(report_lines)
    report_file = output_path / 'analysis_report.md'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    return str(report_file)

def main():
    parser = argparse.ArgumentParser(description="Gelişmiş veri analizi")
    parser.add_argument("--input", required=True, help="Input CSV or JSON file")
    parser.add_argument("--output", default="outputs/analysis", help="Output directory")
    parser.add_argument("--format", choices=["csv", "json"], default="csv", help="Input format")
    
    args = parser.parse_args()
    
    console.print(Panel.fit(
        f"[bold blue]Etsy Data Analysis[/bold blue]\n"
        f"Input: {args.input}\n"
        f"Output: {args.output}",
        title="Configuration"
    ))
    
    try:
        # Load data
        console.print("[yellow]Loading data...[/yellow]")
        df = load_data(args.input)
        console.print(f"[green]Loaded {len(df)} products[/green]")
        
        # Clean data
        console.print("[yellow]Cleaning data...[/yellow]")
        df = clean_price_data(df)
        
        # Create visualizations
        console.print("[yellow]Creating visualizations...[/yellow]")
        create_visualizations(df, args.output)
        
        # Generate report
        console.print("[yellow]Generating report...[/yellow]")
        report_file = generate_report(df, args.output)
        
        # Display summary
        console.print("\n[bold green]Analysis Complete![/bold green]")
        console.print(f"Report saved to: {report_file}")
        console.print(f"Visualizations saved to: {args.output}/")
        
        # Show basic stats
        if 'price_clean' in df.columns:
            price_stats = analyze_pricing(df)
            table = Table(title="Price Statistics")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Mean", f"${price_stats.get('mean', 0):.2f}")
            table.add_row("Median", f"${price_stats.get('median', 0):.2f}")
            table.add_row("Min", f"${df['price_clean'].min():.2f}")
            table.add_row("Max", f"${df['price_clean'].max():.2f}")
            
            console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise

if __name__ == "__main__":
    main()
