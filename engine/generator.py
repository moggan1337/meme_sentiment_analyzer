"""Report generation module."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generates markdown and JSON reports for analyzed coins."""

    def __init__(self, config: dict):
        """Initialize with configuration."""
        self.config = config
        self.output_dir = Path(config.get('reporting', {}).get('output_dir', 'reports'))
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate(self, results: List[dict]) -> Optional[str]:
        """Generate report for qualifying coins."""
        if not results:
            return None

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Generate markdown report
        md_path = self.output_dir / f"report_{timestamp}.md"
        self._generate_markdown(results, md_path)
        
        # Generate JSON report
        json_path = self.output_dir / f"report_{timestamp}.json"
        self._generate_json(results, json_path)
        
        logger.info(f"Generated reports: {md_path}, {json_path}")
        return str(md_path)

    def _generate_markdown(self, results: List[dict], path: Path):
        """Generate markdown report."""
        lines = [
            "# Meme Coin Sentiment Report",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Summary",
            f"- **Coins Analyzed**: {len(results)}",
            f"- **Top Performer**: {results[0]['symbol'] if results else 'N/A'}",
            "",
            "## Detailed Analysis",
            ""
        ]
        
        for i, coin in enumerate(results, 1):
            score = coin.get('score', {})
            lines.extend([
                f"### {i}. {coin['symbol']}",
                f"- **Score**: {score.get('composite', 0):.2f}/100",
                f"- **Sentiment**: {score.get('sentiment', 0):.1f}%",
                f"- **Confidence**: {score.get('confidence', 0):.1f}%",
                f"- **Mentions**: {score.get('mention_count', 0):,} (+{score.get('mention_growth', 0):.1f}%)",
                f"- **Price Change**: {score.get('price_change', 0):+.2f}%",
                f"- **Volume Change**: {score.get('volume_change', 0):+.2f}%",
                ""
            ])
        
        with open(path, 'w') as f:
            f.write('\n'.join(lines))

    def _generate_json(self, results: List[dict], path: Path):
        """Generate JSON report."""
        report = {
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'coins_analyzed': len(results),
                'top_performer': results[0]['symbol'] if results else None
            },
            'coins': results
        }
        
        with open(path, 'w') as f:
            json.dump(report, f, indent=2, default=str)

    def get_latest_report(self) -> Optional[Path]:
        """Get path to most recent report."""
        reports = sorted(self.output_dir.glob("report_*.md"), reverse=True)
        return reports[0] if reports else None
