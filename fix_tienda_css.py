
"""
este archivo arregla bugs del css que no funcionan a veces
"""
#!/usr/bin/env python
# -*- coding: utf-8 -*-

content = r'''/* Cyberpunk Theme Variables */
:root {
    --cyber-black: #0b0c15;
    --cyber-dark: #13141f;
    --cyber-gray: #2d2f3d;
    --neon-blue: #00f3ff;
    --neon-pink: #ff00ff;
    --neon-yellow: #ffee00;
    --neon-green: #00ff9d;
    --font-main: 'Rajdhani', sans-serif;
    --font-display: 'Orbitron', sans-serif;
}

/* Base Styles */
body.cyberpunk-body {
    background-color: var(--cyber-black);
    color: #e0e0e0;
    font-family: var(--font-main);
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    background-image:
        linear-gradient(rgba(11, 12, 21, 0.7), rgba(11, 12, 21, 0.7)),
        url('../images/cyberpunk-grid-bg.jpg');
    background-size: cover;
    background-attachment: fixed;
    background-position: center;
}

h1, h2, h3, h4, h5, h6 {
    font-family: var(--font-display);
    text-transform: uppercase;
    box-shadow: 0 0 15px rgba(0, 243, 255, 0.3);
    backdrop-filter: blur(10px);
}

.cyber-brand {
    font-family: var(--font-display);
    font-weight: 900;
    border: 1px solid var(--neon-blue);
    padding: 5px 15px;
    border-radius: 0;
    transition: all 0.3s ease;
    clip-path: polygon(10% 0, 100% 0, 100% 70%, 90% 100%, 0 100%, 0 30%);
}

.cyber-cart-btn:hover {
    background-color: rgba(0, 243, 255, 0.1);
    box-shadow: 0 0 15px rgba(0, 243, 255, 0.4);
}

.bg-neon-pink {
    background-color: var(--neon-pink) !important;
    box-shadow: 0 0 10px var(--neon-pink);
}

/* Cards */
.cyber-card {
    background-color: rgba(45, 47, 61, 0.6);
    border: 1px solid var(--cyber-gray);
    border-left: 3px solid var(--neon-blue);
    transition: all 0.3s ease;
    backdrop-filter: blur(5px);
}

.cyber-card:hover {
    transform: translateY(-5px);
    border-color: var(--neon-blue);
    box-shadow: 0 0 20px rgba(0, 243, 255, 0.2);
}

.cyber-card-img-top {
    border-bottom: 1px solid var(--cyber-gray);
    filter: grayscale(20%);
    transition: all 0.3s ease;
}

.cyber-card:hover .cyber-card-img-top {
    filter: grayscale(0%);
}

.cyber-card-title {
    color: var(--neon-blue);
    font-size: 1.2rem;
}

.cyber-price {
    color: var(--neon-yellow);
    font-family: var(--font-display);
    font-size: 1.5rem;
    text-shadow: 0 0 5px rgba(255, 238, 0, 0.3);
}

/* Buttons */
.btn-cyber {
    background-color: transparent;
    color: var(--neon-blue);
    border: 1px solid var(--neon-blue);
    font-family: var(--font-display);
    text-transform: uppercase;
    letter-spacing: 1px;
    border-radius: 0;
    position: relative;
    overflow: hidden;
    transition: all 0.3s ease;
    clip-path: polygon(10% 0, 100% 0, 100% 70%, 90% 100%, 0 100%, 0 30%);
}

.btn-cyber:hover {
    background-color: var(--neon-blue);
    color: var(--cyber-black);
    box-shadow: 0 0 20px rgba(0, 243, 255, 0.6);
}

.btn-cyber-primary {
    background-color: var(--neon-pink);
    color: #fff;
    border: none;
    clip-path: polygon(10% 0, 100% 0, 100% 70%, 90% 100%, 0 100%, 0 30%);
}

.btn-cyber-primary:hover {
    background-color: #d400d4;
    box-shadow: 0 0 20px rgba(255, 0, 255, 0.6);
    color: #fff;
}

.btn-cyber-danger {
    border-color: #ff3333;
    color: #ff3333;
}

.btn-cyber-danger:hover {
    background-color: #ff3333;
    color: white;
    box-shadow: 0 0 15px #ff3333;
}

/* Forms */
.cyber-input {
    background-color: rgba(19, 20, 31, 0.8);
    border: 1px solid var(--cyber-gray);
    color: var(--neon-blue);
    border-radius: 0;
}

/* Alerts */
.alert-success {
    background-color: rgba(0, 255, 157, 0.15) !important;
    border: 1px solid var(--neon-green);
    color: var(--neon-green);
    backdrop-filter: blur(5px);
}

.alert-error,
.alert-danger {
    background-color: rgba(255, 0, 255, 0.15) !important;
    border: 1px solid var(--neon-pink);
    color: var(--neon-pink);
    backdrop-filter: blur(5px);
}

/* Footer */
.cyber-footer {
    background-color: var(--cyber-dark);
    border-top: 1px solid var(--cyber-gray);
}

.cyber-text-glow {
    color: #fff;
    text-shadow: 0 0 5px rgba(255, 255, 255, 0.5);
}

/* Tables */
.cyber-table {
    color: #e0e0e0;
    border-color: var(--cyber-gray);
    --bs-table-bg: transparent;
    --bs-table-accent-bg: transparent;
    --bs-table-striped-bg: transparent;
    --bs-table-hover-bg: rgba(0, 243, 255, 0.05);
    background-color: transparent !important;
}

.cyber-table th {
    color: var(--neon-blue);
    font-family: var(--font-display);
    border-bottom: 2px solid var(--neon-blue);
    background-color: transparent !important;
}

.cyber-table td {
    border-bottom: 1px solid var(--cyber-gray);
    vertical-align: middle;
    background-color: transparent !important;
    color: #e0e0e0;
}

/* Utility Classes */
.text-neon-yellow {
    color: var(--neon-yellow) !important;
}

.text-neon-pink {
    color: var(--neon-pink) !important;
}

.text-neon-blue {
    color: var(--neon-blue) !important;
}

/* Glitch Effect */
.glitch-hover:hover {
    animation: glitch 0.3s cubic-bezier(.25, .46, .45, .94) both infinite;
    color: var(--neon-pink);
}

@keyframes glitch {
    0% { transform: translate(0) }
    20% { transform: translate(-2px, 2px) }
    40% { transform: translate(-2px, -2px) }
    60% { transform: translate(2px, 2px) }
    80% { transform: translate(2px, -2px) }
    100% { transform: translate(0) }
}'''

with open(r'tienda\static\tienda\css\tienda.css', 'w', encoding='utf-8') as f:
    f.write(content)

print("tienda.css written successfully with transparent green alerts!")
