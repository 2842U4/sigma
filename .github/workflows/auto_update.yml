name: Auto Fetch Google Trends

on:
  schedule:
    - cron: '0 */2 * * *'
  workflow_dispatch:

permissions:
  contents: write

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repo
        uses: actions/checkout@v4

      - name: Fetch Google Global Trends
        run: python fetch_google_trends.py

      - name: Push updated trends.json
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add trends.json
          git diff --quiet && git diff --staged --quiet || git commit -m "chore: update google trends"
          git push
