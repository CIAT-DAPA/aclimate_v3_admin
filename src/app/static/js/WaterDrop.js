/**
 * WaterDropsBg.js - Animación de gotas de agua mejorada
 * Compatible con el sistema Color4Bg
 */

(function (global) {
  "use strict";

  class WaterDropsBg {
    constructor(options = {}) {
      this.options = {
        dom: options.dom || "body",
        colors: options.colors || ["#4a90e2"], // Color único por defecto
        speed: options.speed || 1,
        density: options.density || 0.5,
        minSize: options.minSize || 1,
        maxSize: options.maxSize || 3,
        loop: options.loop !== false,
        rippleEffect: options.rippleEffect !== false, // Efecto de ondas al tocar el suelo
      };

      this.canvas = null;
      this.ctx = null;
      this.drops = [];
      this.ripples = [];
      this.animationId = null;
      this.container = null;

      this.init();
    }

    init() {
      this.createCanvas();
      this.createDrops();
      if (this.options.loop) {
        this.animate();
      }
      this.bindEvents();
    }

    createCanvas() {
      // Obtener el contenedor
      this.container =
        typeof this.options.dom === "string"
          ? document.getElementById(this.options.dom)
          : this.options.dom;

      if (!this.container) {
        console.warn("WaterDropsBg: Container not found");
        return;
      }

      // Crear canvas
      this.canvas = document.createElement("canvas");
      this.ctx = this.canvas.getContext("2d");

      // Estilos del canvas para que actúe como fondo
      this.canvas.style.position = "absolute";
      this.canvas.style.top = "0";
      this.canvas.style.left = "0";
      this.canvas.style.width = "100%";
      this.canvas.style.height = "100%";
      this.canvas.style.zIndex = "-1";
      this.canvas.style.pointerEvents = "none";

      // Asegurar que el contenedor tenga position relative
      const containerStyle = getComputedStyle(this.container);
      if (containerStyle.position === "static") {
        this.container.style.position = "relative";
      }

      this.container.appendChild(this.canvas);
      this.resize();
    }

    createDrops() {
      this.drops = [];
      this.ripples = [];
      const dropCount = Math.floor(
        ((this.canvas.width * this.canvas.height) / 8000) * this.options.density
      );

      for (let i = 0; i < dropCount; i++) {
        this.drops.push(this.createDrop());
      }
    }

    createDrop() {
      const size =
        Math.random() * (this.options.maxSize - this.options.minSize) +
        this.options.minSize;

      // Usar un solo color base con variaciones sutiles de transparencia
      const baseColor = this.options.colors[0] || "#4a90e2";

      return {
        x: Math.random() * this.canvas.width,
        y: Math.random() * -this.canvas.height * 0.5 - size * 2, // Distribuir más arriba
        size: size,
        speed: (Math.random() * 1.5 + 0.5) * this.options.speed,
        color: baseColor,
        opacity: Math.random() * 0.4 + 0.6, // Más consistente
        wobble: Math.random() * Math.PI * 2,
        wobbleSpeed: Math.random() * 0.01 + 0.005,
        length: size * (Math.random() * 3 + 2), // Longitud de la gota
      };
    }

    createRipple(x, y) {
      return {
        x: x,
        y: y,
        radiusX: 0,
        radiusY: 0,
        maxRadiusX: Math.random() * 15 + 20, // Siempre más ancho (20-35px)
        maxRadiusY: Math.random() * 4 + 3, // Siempre más estrecho (3-7px)
        opacity: 0.6,
        color: this.options.colors[0] || "#4a90e2",
        growthX: Math.random() * 0.8 + 1.0, // Crecimiento consistente en X (1.0-1.8)
        growthY: Math.random() * 0.3 + 0.2, // Crecimiento muy lento en Y (0.2-0.5)
      };
    }

    drawDrop(drop) {
      this.ctx.save();

      // Crear gradiente linear para simular una gota alargada
      const gradient = this.ctx.createLinearGradient(
        drop.x,
        drop.y - drop.length / 2,
        drop.x,
        drop.y + drop.length / 2
      );

      gradient.addColorStop(0, this.hexToRgba(drop.color, 0));
      gradient.addColorStop(
        0.1,
        this.hexToRgba(drop.color, drop.opacity * 0.3)
      );
      gradient.addColorStop(
        0.8,
        this.hexToRgba(drop.color, drop.opacity * 0.8)
      );
      gradient.addColorStop(1, this.hexToRgba(drop.color, drop.opacity));

      this.ctx.fillStyle = gradient;

      // Dibujar gota alargada más realista
      this.ctx.beginPath();
      this.ctx.ellipse(
        drop.x + Math.sin(drop.wobble) * 0.5,
        drop.y,
        drop.size * 0.3, // Más delgada
        drop.length * 0.5, // Más alargada
        0,
        0,
        Math.PI * 2
      );
      this.ctx.fill();

      this.ctx.restore();
    }

    drawRipple(ripple) {
      if (ripple.radiusX >= ripple.maxRadiusX) return;

      this.ctx.save();
      this.ctx.strokeStyle = this.hexToRgba(ripple.color, ripple.opacity);
      this.ctx.lineWidth = 1;
      this.ctx.beginPath();
      // Dibujar elipse ovalada (más ancha que alta)
      this.ctx.ellipse(
        ripple.x,
        ripple.y,
        ripple.radiusX,
        ripple.radiusY,
        0,
        0,
        Math.PI * 2
      );
      this.ctx.stroke();
      this.ctx.restore();
    }

    updateDrop(drop) {
      drop.y += drop.speed;
      drop.wobble += drop.wobbleSpeed;

      // Si la gota toca el suelo, crear ondas y reposicionar
      if (drop.y >= this.canvas.height - 10) {
        if (this.options.rippleEffect) {
          this.ripples.push(this.createRipple(drop.x, this.canvas.height - 5));
        }

        // Reposicionar la gota
        drop.y = Math.random() * -this.canvas.height * 0.3 - drop.length; // Más variedad en altura inicial
        drop.x = Math.random() * this.canvas.width;
        drop.speed = (Math.random() * 1.5 + 0.5) * this.options.speed;
      }
    }

    updateRipple(ripple) {
      ripple.radiusX += ripple.growthX;
      ripple.radiusY += ripple.growthY;
      ripple.opacity *= 0.96; // Fade out un poco más rápido
    }

    animate() {
      this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

      // Actualizar y dibujar gotas
      this.drops.forEach((drop) => {
        this.updateDrop(drop);
        this.drawDrop(drop);
      });

      // Actualizar y dibujar ondas
      this.ripples = this.ripples.filter((ripple) => {
        this.updateRipple(ripple);
        if (ripple.opacity > 0.01 && ripple.radiusX < ripple.maxRadiusX) {
          this.drawRipple(ripple);
          return true;
        }
        return false;
      });

      if (this.options.loop) {
        this.animationId = requestAnimationFrame(() => this.animate());
      }
    }

    resize() {
      if (!this.canvas || !this.container) return;

      const rect = this.container.getBoundingClientRect();
      this.canvas.width = rect.width;
      this.canvas.height = rect.height;

      // Recrear gotas después del resize
      this.createDrops();
    }

    bindEvents() {
      window.addEventListener("resize", () => this.resize());
    }

    hexToRgba(hex, alpha) {
      const r = parseInt(hex.slice(1, 3), 16);
      const g = parseInt(hex.slice(3, 5), 16);
      const b = parseInt(hex.slice(5, 7), 16);
      return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    }

    destroy() {
      if (this.animationId) {
        cancelAnimationFrame(this.animationId);
      }
      if (this.canvas && this.canvas.parentNode) {
        this.canvas.parentNode.removeChild(this.canvas);
      }
      window.removeEventListener("resize", () => this.resize());
    }

    // Métodos de compatibilidad con Color4Bg
    pause() {
      if (this.animationId) {
        cancelAnimationFrame(this.animationId);
        this.animationId = null;
      }
    }

    resume() {
      if (!this.animationId && this.options.loop) {
        this.animate();
      }
    }

    updateColors(colors) {
      this.options.colors = colors;
      this.drops.forEach((drop) => {
        drop.color = colors[0] || "#4a90e2"; // Usar solo el primer color
      });
    }
  }

  // Exportar para uso global (compatible con Color4Bg)
  if (!global.Color4Bg) {
    global.Color4Bg = {};
  }
  global.Color4Bg.WaterDropsBg = WaterDropsBg;

  // También disponible como constructor independiente
  global.WaterDropsBg = WaterDropsBg;
})(typeof window !== "undefined" ? window : this);
