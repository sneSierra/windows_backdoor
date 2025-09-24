#!/usr/bin/env python3
"""
NatureSearch - Standalone Executable
A complete nature-themed search engine in a single file
"""

import os
import sys
import threading
import time
import webbrowser
import json
import random
import socket
from urllib.parse import urljoin, urlparse, unquote
import http.server
import socketserver
from io import StringIO

# Flask and related imports
try:
    from flask import Flask, request, jsonify, send_from_directory, render_template_string
    from flask_cors import CORS
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Installing required packages...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "flask", "flask-cors", "requests", "beautifulsoup4"])
    from flask import Flask, request, jsonify, send_from_directory, render_template_string
    from flask_cors import CORS
    import requests
    from bs4 import BeautifulSoup

# Embedded HTML template
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NatureSearch - Natural Web Search</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        /* Embedded CSS */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #2E8B57 0%, #228B22 25%, #32CD32 50%, #90EE90 75%, #F0FFF0 100%);
            min-height: 100vh;
            color: #2F4F2F;
            line-height: 1.6;
            overflow-x: hidden;
            position: relative;
        }

        .particles-container {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 1;
        }

        .particle {
            position: absolute;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 50%;
            animation: float 6s ease-in-out infinite;
        }

        @keyframes float {
            0%, 100% {
                transform: translateY(100vh) rotate(0deg);
                opacity: 0;
            }
            10% {
                opacity: 1;
            }
            90% {
                opacity: 1;
            }
            50% {
                transform: translateY(-20vh) rotate(180deg);
            }
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            position: relative;
            z-index: 2;
        }

        .main {
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 2rem 2rem 4rem;
            position: relative;
        }

        .logo-container {
            text-align: center;
            margin-bottom: 3rem;
            animation: logoEntrance 1.5s ease-out;
        }

        .logo {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 1rem;
            font-size: 4rem;
            font-weight: 700;
            color: #2F4F2F;
            margin-bottom: 0.5rem;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
        }

        .logo-icon {
            font-size: 4.5rem;
            color: #228B22;
            animation: leafSway 3s ease-in-out infinite;
            filter: drop-shadow(2px 2px 4px rgba(0, 0, 0, 0.1));
        }

        .logo-text {
            background: linear-gradient(45deg, #228B22, #32CD32, #90EE90);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: textGlow 2s ease-in-out infinite alternate;
        }

        .logo-subtitle {
            font-size: 1.2rem;
            color: #556B2F;
            font-weight: 300;
            opacity: 0.8;
            animation: fadeInUp 1.8s ease-out;
        }

        @keyframes logoEntrance {
            0% {
                opacity: 0;
                transform: translateY(-50px) scale(0.8);
            }
            100% {
                opacity: 1;
                transform: translateY(0) scale(1);
            }
        }

        @keyframes leafSway {
            0%, 100% {
                transform: rotate(-5deg);
            }
            50% {
                transform: rotate(5deg);
            }
        }

        @keyframes textGlow {
            0% {
                text-shadow: 0 0 5px rgba(34, 139, 34, 0.3);
            }
            100% {
                text-shadow: 0 0 20px rgba(34, 139, 34, 0.6);
            }
        }

        @keyframes fadeInUp {
            0% {
                opacity: 0;
                transform: translateY(20px);
            }
            100% {
                opacity: 0.8;
                transform: translateY(0);
            }
        }

        .search-container {
            width: 100%;
            max-width: 600px;
            text-align: center;
            margin-bottom: 2rem;
            animation: searchEntrance 2s ease-out;
        }

        @keyframes searchEntrance {
            0% {
                opacity: 0;
                transform: translateY(30px);
            }
            100% {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .search-box {
            position: relative;
            margin-bottom: 2rem;
        }

        .search-box input {
            width: 100%;
            padding: 1.2rem 3.5rem 1.2rem 3.5rem;
            font-size: 1.1rem;
            border: 3px solid rgba(34, 139, 34, 0.3);
            border-radius: 50px;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            outline: none;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 8px 32px rgba(34, 139, 34, 0.2);
            color: #2F4F2F;
        }

        .search-box input:focus {
            border-color: #228B22;
            box-shadow: 0 12px 40px rgba(34, 139, 34, 0.4);
            transform: translateY(-3px) scale(1.02);
        }

        .search-box input::placeholder {
            color: #90EE90;
            font-weight: 300;
        }

        .search-icon {
            position: absolute;
            left: 1.5rem;
            top: 50%;
            transform: translateY(-50%);
            color: #228B22;
            font-size: 1.2rem;
            transition: all 0.3s ease;
        }

        .voice-search {
            position: absolute;
            right: 1.5rem;
            top: 50%;
            transform: translateY(-50%);
            background: linear-gradient(45deg, #228B22, #32CD32);
            border: none;
            color: white;
            cursor: pointer;
            padding: 0.8rem;
            border-radius: 50%;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 4px 15px rgba(34, 139, 34, 0.3);
        }

        .voice-search:hover {
            background: linear-gradient(45deg, #32CD32, #90EE90);
            transform: translateY(-50%) scale(1.1);
            box-shadow: 0 6px 20px rgba(34, 139, 34, 0.4);
        }

        .search-buttons {
            display: flex;
            gap: 1rem;
            justify-content: center;
            margin-bottom: 2rem;
        }

        .btn {
            padding: 1rem 2.5rem;
            border: none;
            border-radius: 50px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            text-decoration: none;
            display: inline-block;
            position: relative;
            overflow: hidden;
        }

        .btn-primary {
            background: linear-gradient(45deg, #228B22, #32CD32);
            color: white;
            box-shadow: 0 6px 20px rgba(34, 139, 34, 0.4);
        }

        .btn-primary:hover {
            background: linear-gradient(45deg, #32CD32, #90EE90);
            transform: translateY(-3px) scale(1.05);
            box-shadow: 0 8px 25px rgba(34, 139, 34, 0.5);
        }

        .btn-secondary {
            background: rgba(255, 255, 255, 0.9);
            color: #2F4F2F;
            border: 2px solid rgba(34, 139, 34, 0.3);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }

        .btn-secondary:hover {
            background: rgba(255, 255, 255, 1);
            border-color: #228B22;
            transform: translateY(-3px) scale(1.05);
            box-shadow: 0 6px 20px rgba(34, 139, 34, 0.3);
        }

        .search-nav {
            display: flex;
            gap: 1rem;
            justify-content: center;
            margin-bottom: 2rem;
            animation: navEntrance 2.2s ease-out;
        }

        @keyframes navEntrance {
            0% {
                opacity: 0;
                transform: translateY(20px);
            }
            100% {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .nav-link {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.8rem 1.5rem;
            text-decoration: none;
            color: #556B2F;
            font-weight: 500;
            border-radius: 25px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            background: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(10px);
            border: 2px solid transparent;
        }

        .nav-link:hover {
            background: rgba(255, 255, 255, 0.9);
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(34, 139, 34, 0.2);
        }

        .nav-link.active {
            background: linear-gradient(45deg, #228B22, #32CD32);
            color: white;
            box-shadow: 0 4px 15px rgba(34, 139, 34, 0.4);
        }

        .search-suggestions {
            width: 100%;
            max-width: 600px;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(15px);
            border-radius: 20px;
            box-shadow: 0 8px 32px rgba(34, 139, 34, 0.2);
            margin-bottom: 2rem;
            display: none;
            animation: suggestionsEntrance 0.3s ease-out;
        }

        @keyframes suggestionsEntrance {
            0% {
                opacity: 0;
                transform: translateY(-10px) scale(0.95);
            }
            100% {
                opacity: 1;
                transform: translateY(0) scale(1);
            }
        }

        .suggestion-item {
            padding: 1.2rem 1.5rem;
            cursor: pointer;
            border-bottom: 1px solid rgba(34, 139, 34, 0.1);
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 1rem;
            position: relative;
            overflow: hidden;
        }

        .suggestion-item:last-child {
            border-bottom: none;
        }

        .suggestion-item:hover {
            background: rgba(34, 139, 34, 0.05);
            transform: translateX(5px);
        }

        .suggestion-icon {
            color: #228B22;
            font-size: 1rem;
            z-index: 1;
            position: relative;
        }

        .search-results {
            width: 100%;
            max-width: 800px;
            display: none;
            animation: resultsEntrance 0.5s ease-out;
        }

        @keyframes resultsEntrance {
            0% {
                opacity: 0;
                transform: translateY(20px);
            }
            100% {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .result-item {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(15px);
            padding: 2rem;
            margin-bottom: 1.5rem;
            border-radius: 20px;
            box-shadow: 0 8px 32px rgba(34, 139, 34, 0.15);
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            border: 1px solid rgba(34, 139, 34, 0.1);
        }

        .result-item:hover {
            transform: translateY(-5px) scale(1.02);
            box-shadow: 0 12px 40px rgba(34, 139, 34, 0.25);
        }

        .result-title {
            font-size: 1.3rem;
            font-weight: 600;
            color: #1B4D3E;
            text-decoration: none;
            margin-bottom: 0.8rem;
            display: block;
            transition: color 0.3s ease;
        }

        .result-title:hover {
            color: #228B22;
            text-decoration: underline;
        }

        .result-url {
            color: #228B22;
            font-size: 0.9rem;
            margin-bottom: 0.8rem;
            font-weight: 500;
        }

        .result-description {
            color: #556B2F;
            line-height: 1.6;
        }

        .quick-links {
            width: 100%;
            max-width: 600px;
            margin-top: 3rem;
            animation: quickLinksEntrance 2.5s ease-out;
        }

        @keyframes quickLinksEntrance {
            0% {
                opacity: 0;
                transform: translateY(30px);
            }
            100% {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .quick-links h3 {
            text-align: center;
            color: #2F4F2F;
            margin-bottom: 2rem;
            font-weight: 600;
            font-size: 1.5rem;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .quick-link-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 1.5rem;
        }

        .quick-link {
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(15px);
            padding: 2rem 1.5rem;
            border-radius: 20px;
            text-decoration: none;
            color: #2F4F2F;
            text-align: center;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 6px 20px rgba(34, 139, 34, 0.15);
            border: 2px solid transparent;
        }

        .quick-link:hover {
            transform: translateY(-8px) scale(1.05);
            box-shadow: 0 12px 30px rgba(34, 139, 34, 0.25);
            background: rgba(255, 255, 255, 1);
            border-color: #228B22;
        }

        .quick-link i {
            font-size: 2rem;
            color: #228B22;
            margin-bottom: 1rem;
            display: block;
            transition: all 0.3s ease;
        }

        .quick-link:hover i {
            transform: scale(1.2) rotate(5deg);
            color: #32CD32;
        }

        .footer {
            background: rgba(47, 79, 47, 0.9);
            backdrop-filter: blur(15px);
            padding: 2rem;
            text-align: center;
            box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.1);
            animation: footerEntrance 3s ease-out;
        }

        @keyframes footerEntrance {
            0% {
                opacity: 0;
                transform: translateY(20px);
            }
            100% {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .footer-links {
            display: flex;
            justify-content: center;
            gap: 2rem;
            margin-bottom: 1rem;
            flex-wrap: wrap;
        }

        .footer-links a {
            color: #90EE90;
            text-decoration: none;
            font-size: 0.9rem;
            transition: all 0.3s ease;
            padding: 0.5rem 1rem;
            border-radius: 20px;
        }

        .footer-links a:hover {
            color: white;
            background: rgba(255, 255, 255, 0.1);
            transform: translateY(-2px);
        }

        .footer-info {
            color: #90EE90;
            font-size: 0.8rem;
            opacity: 0.8;
        }

        @media (max-width: 768px) {
            .main { padding: 1rem 1rem 3rem; }
            .logo { font-size: 3rem; gap: 0.8rem; }
            .logo-icon { font-size: 3.5rem; }
            .search-buttons { flex-direction: column; align-items: center; gap: 1rem; }
            .btn { width: 200px; }
            .search-nav { flex-wrap: wrap; gap: 0.8rem; }
        }

        .loading {
            display: inline-block;
            width: 24px;
            height: 24px;
            border: 3px solid rgba(34, 139, 34, 0.3);
            border-radius: 50%;
            border-top-color: #228B22;
            animation: spin 1s ease-in-out infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .fade-in {
            animation: fadeIn 0.6s ease-in-out;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        html {
            scroll-behavior: smooth;
        }

        ::-webkit-scrollbar {
            width: 8px;
        }

        ::-webkit-scrollbar-track {
            background: rgba(34, 139, 34, 0.1);
        }

        ::-webkit-scrollbar-thumb {
            background: linear-gradient(180deg, #228B22, #32CD32);
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="particles-container">
            <div class="particle"></div>
            <div class="particle"></div>
            <div class="particle"></div>
            <div class="particle"></div>
            <div class="particle"></div>
            <div class="particle"></div>
            <div class="particle"></div>
            <div class="particle"></div>
        </div>

        <main class="main">
            <div class="logo-container">
                <div class="logo">
                    <i class="fas fa-leaf logo-icon"></i>
                    <span class="logo-text">NatureSearch</span>
                </div>
                <div class="logo-subtitle">Search the web naturally</div>
            </div>
            
            <div class="search-container">
                <div class="search-box">
                    <i class="fas fa-search search-icon"></i>
                    <input type="text" id="searchInput" placeholder="Search the web..." autocomplete="off">
                    <button class="voice-search" title="Search by voice">
                        <i class="fas fa-microphone"></i>
                    </button>
                </div>
                <div class="search-buttons">
                    <button class="btn btn-primary" id="searchBtn">Search</button>
                    <button class="btn btn-secondary" id="luckyBtn">I'm Feeling Lucky</button>
                </div>
                
                <nav class="search-nav">
                    <a href="#" class="nav-link active" data-type="web">
                        <i class="fas fa-globe"></i>
                        <span>Web</span>
                    </a>
                    <a href="#" class="nav-link" data-type="images">
                        <i class="fas fa-image"></i>
                        <span>Images</span>
                    </a>
                    <a href="#" class="nav-link" data-type="news">
                        <i class="fas fa-newspaper"></i>
                        <span>News</span>
                    </a>
                    <a href="#" class="nav-link" data-type="videos">
                        <i class="fas fa-video"></i>
                        <span>Videos</span>
                    </a>
                </nav>
            </div>

            <div class="search-suggestions" id="suggestions"></div>
            <div class="search-results" id="searchResults"></div>

            <div class="quick-links">
                <h3>Explore Nature</h3>
                <div class="quick-link-grid">
                    <a href="#" class="quick-link" data-search="forest conservation">
                        <i class="fas fa-tree"></i>
                        <span>Forests</span>
                    </a>
                    <a href="#" class="quick-link" data-search="wildlife photography">
                        <i class="fas fa-paw"></i>
                        <span>Wildlife</span>
                    </a>
                    <a href="#" class="quick-link" data-search="national parks">
                        <i class="fas fa-mountain"></i>
                        <span>Parks</span>
                    </a>
                    <a href="#" class="quick-link" data-search="ocean conservation">
                        <i class="fas fa-water"></i>
                        <span>Oceans</span>
                    </a>
                    <a href="#" class="quick-link" data-search="climate change">
                        <i class="fas fa-cloud-sun"></i>
                        <span>Climate</span>
                    </a>
                    <a href="#" class="quick-link" data-search="sustainable living">
                        <i class="fas fa-recycle"></i>
                        <span>Eco Living</span>
                    </a>
                </div>
            </div>
        </main>

        <footer class="footer">
            <div class="footer-links">
                <a href="#">About NatureSearch</a>
                <a href="#">Privacy</a>
                <a href="#">Terms</a>
                <a href="#">Settings</a>
                <a href="#">Help</a>
            </div>
            <div class="footer-info">
                <span>&copy; 2024 NatureSearch. Standalone Edition</span>
            </div>
        </footer>
    </div>

    <script>
        // Embedded JavaScript
        class NatureSearchEngine {
            constructor() {
                this.searchInput = document.getElementById('searchInput');
                this.searchBtn = document.getElementById('searchBtn');
                this.luckyBtn = document.getElementById('luckyBtn');
                this.suggestions = document.getElementById('suggestions');
                this.searchResults = document.getElementById('searchResults');
                this.voiceSearch = document.querySelector('.voice-search');
                
                this.init();
            }
            
            init() {
                this.setupEventListeners();
                this.setupParticleAnimation();
            }
            
            setupEventListeners() {
                this.searchInput.addEventListener('input', (e) => {
                    this.handleInput(e.target.value);
                });
                
                this.searchInput.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') {
                        this.performSearch(e.target.value);
                    }
                });
                
                this.searchBtn.addEventListener('click', () => {
                    this.performSearch(this.searchInput.value);
                });
                
                this.luckyBtn.addEventListener('click', () => {
                    this.performLuckySearch(this.searchInput.value);
                });
                
                document.querySelectorAll('.nav-link').forEach(link => {
                    link.addEventListener('click', (e) => {
                        e.preventDefault();
                        this.setActiveNav(link);
                    });
                });
                
                document.querySelectorAll('.quick-link').forEach(link => {
                    link.addEventListener('click', (e) => {
                        e.preventDefault();
                        this.handleQuickLink(link);
                    });
                });
            }
            
            setupParticleAnimation() {
                const particles = document.querySelectorAll('.particle');
                particles.forEach((particle, index) => {
                    const sizes = [6, 8, 10, 12, 14, 16];
                    const size = sizes[Math.floor(Math.random() * sizes.length)];
                    particle.style.width = size + 'px';
                    particle.style.height = size + 'px';
                    particle.style.left = Math.random() * 100 + '%';
                    particle.style.animationDelay = Math.random() * 5 + 's';
                    particle.style.animationDuration = (6 + Math.random() * 6) + 's';
                });
            }
            
            async handleInput(value) {
                if (value.length > 0) {
                    this.showSuggestions();
                    await this.getSuggestions(value);
                } else {
                    this.hideSuggestions();
                }
            }
            
            showSuggestions() {
                this.suggestions.style.display = 'block';
            }
            
            hideSuggestions() {
                this.suggestions.style.display = 'none';
            }
            
            async getSuggestions(query) {
                try {
                    const response = await fetch(`/api/suggestions?q=${encodeURIComponent(query)}`);
                    if (response.ok) {
                        const data = await response.json();
                        this.renderSuggestions(data.suggestions.slice(0, 5));
                    }
                } catch (error) {
                    console.error('Suggestions error:', error);
                    this.filterSuggestions(query);
                }
            }
            
            filterSuggestions(query) {
                const suggestions = [
                    { text: `${query} tutorial`, icon: 'fas fa-graduation-cap' },
                    { text: `${query} guide`, icon: 'fas fa-book' },
                    { text: `${query} news`, icon: 'fas fa-newspaper' },
                    { text: `${query} tips`, icon: 'fas fa-lightbulb' },
                    { text: `${query} reviews`, icon: 'fas fa-star' }
                ];
                this.renderSuggestions(suggestions);
            }
            
            renderSuggestions(suggestions) {
                this.suggestions.innerHTML = suggestions.map(item => `
                    <div class="suggestion-item" onclick="searchEngine.selectSuggestion('${item.text}')">
                        <i class="${item.icon} suggestion-icon"></i>
                        <span>${item.text}</span>
                    </div>
                `).join('');
            }
            
            selectSuggestion(text) {
                this.searchInput.value = text;
                this.hideSuggestions();
                this.performSearch(text);
            }
            
            async performSearch(query) {
                if (!query.trim()) return;
                
                this.hideSuggestions();
                this.showLoading();
                
                try {
                    const searchType = this.getCurrentSearchType();
                    const response = await fetch(`/api/search?q=${encodeURIComponent(query)}&type=${searchType}&limit=10`);
                    
                    if (response.ok) {
                        const data = await response.json();
                        this.displayResults(query, data.results);
                    } else {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                } catch (error) {
                    console.error('Search error:', error);
                    this.displayError(query, error.message);
                } finally {
                    this.hideLoading();
                }
            }
            
            performLuckySearch(query) {
                if (!query.trim()) return;
                this.showNotification('Lucky search would redirect to the first result!', 'info');
            }
            
            displayResults(query, results) {
                this.searchResults.style.display = 'block';
                this.searchResults.classList.add('fade-in');
                
                const searchType = this.getCurrentSearchType();
                
                if (!results || results.length === 0) {
                    this.searchResults.innerHTML = `
                        <div class="result-item">
                            <h3>No results found for "${query}"</h3>
                            <p>Try different keywords or check your spelling.</p>
                        </div>
                    `;
                } else {
                    this.searchResults.innerHTML = `
                        <div class="result-item">
                            <h3>Search results for "${query}" (${searchType})</h3>
                            <p>Found ${results.length} result(s)</p>
                        </div>
                        ${results.map((result, index) => `
                            <div class="result-item" style="animation-delay: ${(index + 1) * 0.1}s">
                                <a href="${result.url}" target="_blank" class="result-title">${result.title}</a>
                                <div class="result-url">${result.url}</div>
                                <div class="result-description">${result.description}</div>
                            </div>
                        `).join('')}
                    `;
                }
            }
            
            displayError(query, message) {
                this.searchResults.style.display = 'block';
                this.searchResults.innerHTML = `
                    <div class="result-item">
                        <h3>Search Error</h3>
                        <p>${message}</p>
                        <p>Query: "${query}"</p>
                    </div>
                `;
            }
            
            getCurrentSearchType() {
                const activeNav = document.querySelector('.nav-link.active');
                return activeNav ? activeNav.getAttribute('data-type') || 'web' : 'web';
            }
            
            showLoading() {
                this.searchBtn.innerHTML = '<div class="loading"></div>';
                this.searchBtn.disabled = true;
            }
            
            hideLoading() {
                this.searchBtn.innerHTML = 'Search';
                this.searchBtn.disabled = false;
            }
            
            setActiveNav(activeLink) {
                document.querySelectorAll('.nav-link').forEach(link => {
                    link.classList.remove('active');
                });
                activeLink.classList.add('active');
                
                this.searchResults.style.display = 'none';
                this.searchResults.innerHTML = '';
            }
            
            handleQuickLink(link) {
                const searchTerm = link.getAttribute('data-search') || link.querySelector('span').textContent;
                this.searchInput.value = searchTerm;
                this.performSearch(searchTerm);
            }
            
            showNotification(message, type = 'info') {
                const notification = document.createElement('div');
                notification.className = `notification notification-${type}`;
                notification.innerHTML = `
                    <i class="fas fa-${type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
                    <span>${message}</span>
                `;
                
                notification.style.cssText = `
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: ${type === 'error' ? '#e74c3c' : '#228B22'};
                    color: white;
                    padding: 1rem 1.5rem;
                    border-radius: 12px;
                    box-shadow: 0 8px 25px rgba(34, 139, 34, 0.3);
                    z-index: 1000;
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                    animation: slideInRight 0.4s ease-out;
                    backdrop-filter: blur(10px);
                `;
                
                document.body.appendChild(notification);
                
                setTimeout(() => {
                    notification.style.animation = 'slideOutRight 0.3s ease-in';
                    setTimeout(() => {
                        if (document.body.contains(notification)) {
                            document.body.removeChild(notification);
                        }
                    }, 300);
                }, 3000);
            }
        }

        // Add notification animations
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideInRight {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            
            @keyframes slideOutRight {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(100%); opacity: 0; }
            }
        `;
        document.head.appendChild(style);

        // Initialize
        document.addEventListener('DOMContentLoaded', () => {
            window.searchEngine = new NatureSearchEngine();
        });
    </script>
</body>
</html>"""


class NatureSearchEngine:
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]
        
    def get_headers(self):
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
    
    def search_web(self, query, num_results=10):
        """Search the web using DuckDuckGo"""
        try:
            search_url = f"https://duckduckgo.com/html/?q={query}"
            response = requests.get(search_url, headers=self.get_headers(), timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                results = self.parse_duckduckgo_results(soup, num_results)
                if results:
                    return results
        except Exception as e:
            print(f"Search error: {e}")
        
        return self.get_mock_results(query, num_results)
    
    def parse_duckduckgo_results(self, soup, num_results):
        """Parse DuckDuckGo search results"""
        results = []
        
        result_containers = soup.find_all('div', class_='result')
        
        for container in result_containers[:num_results]:
            try:
                title_link = container.find('a', class_='result__a')
                if not title_link:
                    continue
                
                title = title_link.get_text(strip=True)
                url = title_link.get('href', '')
                
                description_elem = container.find('a', class_='result__snippet')
                description = description_elem.get_text(strip=True) if description_elem else ''
                
                if title and url:
                    results.append({
                        'title': title,
                        'url': url,
                        'description': description
                    })
                    
            except Exception as e:
                print(f"Error parsing result: {e}")
                continue
        
        return results
    
    def get_suggestions(self, query):
        """Get search suggestions based on query"""
        suggestions = [
            {'text': f'{query} tutorial', 'icon': 'fas fa-graduation-cap'},
            {'text': f'{query} guide', 'icon': 'fas fa-book'},
            {'text': f'{query} examples', 'icon': 'fas fa-code'},
            {'text': f'{query} tips', 'icon': 'fas fa-lightbulb'},
            {'text': f'{query} news', 'icon': 'fas fa-newspaper'},
            {'text': f'{query} reviews', 'icon': 'fas fa-star'},
            {'text': f'{query} comparison', 'icon': 'fas fa-balance-scale'},
            {'text': f'{query} alternatives', 'icon': 'fas fa-exchange-alt'}
        ]
        
        filtered = [s for s in suggestions if query.lower() in s['text'].lower()]
        return filtered[:8] if filtered else suggestions[:5]
    
    def get_mock_results(self, query, num_results=10):
        """Enhanced mock results with nature theme"""
        nature_results = [
            {
                'title': f'NatureSearch Results for "{query}"',
                'url': 'https://naturesearch.example.com',
                'description': f'Discover comprehensive information about {query} with our nature-focused search engine. Find environmental resources, conservation data, and sustainable living tips.'
            },
            {
                'title': f'Environmental Guide to {query}',
                'url': 'https://environment.example.com',
                'description': f'Learn about the environmental impact and conservation aspects of {query}. Includes scientific research, sustainability practices, and eco-friendly alternatives.'
            },
            {
                'title': f'{query} - Wildlife and Conservation',
                'url': 'https://wildlife.example.com',
                'description': f'Explore how {query} relates to wildlife conservation efforts, habitat protection, and biodiversity preservation initiatives worldwide.'
            },
            {
                'title': f'Sustainable {query} Solutions',
                'url': 'https://sustainability.example.com',
                'description': f'Discover sustainable approaches to {query} that promote environmental health, reduce carbon footprint, and support green living practices.'
            },
            {
                'title': f'Nature Photography: {query}',
                'url': 'https://naturephoto.example.com',
                'description': f'Stunning nature photography featuring {query}. Tips for capturing natural beauty, wildlife behavior, and landscape composition techniques.'
            }
        ]
        
        return nature_results[:num_results]


def find_free_port():
    """Find a free port for the server"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port


def create_app():
    """Create Flask application"""
    app = Flask(__name__)
    CORS(app)
    
    # Initialize search engine
    search_engine = NatureSearchEngine()
    
    @app.route('/')
    def index():
        """Serve the main HTML page"""
        return render_template_string(HTML_TEMPLATE)
    
    @app.route('/api/search', methods=['GET'])
    def search():
        """Main search endpoint"""
        query = request.args.get('q', '')
        search_type = request.args.get('type', 'web')
        num_results = int(request.args.get('limit', 10))
        
        if not query:
            return jsonify({'error': 'Query parameter is required'}), 400
        
        try:
            if search_type in ['web', 'images', 'videos', 'news']:
                results = search_engine.search_web(query, num_results)
            else:
                return jsonify({'error': 'Invalid search type'}), 400
            
            return jsonify({
                'query': query,
                'type': search_type,
                'results': results,
                'count': len(results)
            })
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/suggestions', methods=['GET'])
    def suggestions():
        """Get search suggestions"""
        query = request.args.get('q', '')
        
        if not query:
            return jsonify({'suggestions': []})
        
        try:
            suggestions = search_engine.get_suggestions(query)
            return jsonify({'suggestions': suggestions})
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/health', methods=['GET'])
    def health():
        """Health check endpoint"""
        return jsonify({'status': 'healthy', 'message': 'NatureSearch is running'})
    
    return app


def main():
    """Main function to run the standalone application"""
    print("🌿 NatureSearch - Standalone Edition")
    print("=" * 50)
    
    # Check if required packages are available, install if not
    try:
        import flask
        import requests
        from bs4 import BeautifulSoup
        from flask_cors import CORS
        print("✅ All required packages available")
    except ImportError:
        print("📦 Installing required packages...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "flask", "flask-cors", "requests", "beautifulsoup4"])
        print("✅ Packages installed successfully")
    
    # Find available port
    port = find_free_port()
    
    # Create Flask app
    app = create_app()
    
    print(f"🌐 Starting NatureSearch on http://localhost:{port}")
    print("🎯 Features:")
    print("   • Web search with DuckDuckGo integration")
    print("   • Nature-themed interface")
    print("   • Search suggestions")
    print("   • Responsive design")
    print("   • All-in-one executable")
    print("=" * 50)
    print("🔗 Access your search engine at the URL above")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Open browser automatically
    def open_browser():
        time.sleep(2)
        webbrowser.open(f'http://localhost:{port}')
    
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    try:
        app.run(host='0.0.0.0', port=port, debug=False)
    except KeyboardInterrupt:
        print("\n🛑 NatureSearch stopped by user")
        sys.exit(0)


if __name__ == "__main__":
    main()
