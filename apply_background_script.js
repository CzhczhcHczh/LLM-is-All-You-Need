// 应用主页背景和标题栏的脚本
const fs = require('fs');
const path = require('path');

// 主页背景样式
const backgroundStyles = `
.phase-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #e8f4fd 25%, #f0f8ff 50%, #e6f3ff 75%, #f8fafc 100%);
  position: relative;
  overflow: hidden;
}

/* 粒子背景动画 */
.particles-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
}

.particle {
  position: absolute;
  width: 6px;
  height: 6px;
  background: radial-gradient(circle, rgba(64, 158, 255, 1) 0%, rgba(64, 158, 255, 0.4) 50%, transparent 100%);
  border-radius: 50%;
  animation: float linear infinite;
}

.particle:nth-child(2n) {
  background: radial-gradient(circle, rgba(103, 194, 58, 1) 0%, rgba(103, 194, 58, 0.4) 50%, transparent 100%);
  width: 5px;
  height: 5px;
}

.particle:nth-child(3n) {
  background: radial-gradient(circle, rgba(255, 193, 7, 1) 0%, rgba(255, 193, 7, 0.4) 50%, transparent 100%);
  width: 7px;
  height: 7px;
}

.particle:nth-child(4n) {
  background: radial-gradient(circle, rgba(245, 108, 108, 1) 0%, rgba(245, 108, 108, 0.4) 50%, transparent 100%);
  width: 4px;
  height: 4px;
}

@keyframes float {
  0% {
    transform: translateY(100vh) rotate(0deg);
    opacity: 0;
  }
  10% {
    opacity: 1;
  }
  90% {
    opacity: 1;
  }
  100% {
    transform: translateY(-100px) rotate(360deg);
    opacity: 0;
  }
}

/* 标题栏样式 */
.app-header {
  background: #304156;
  color: #fff;
  padding: 0 0 0 32px;
  height: 64px;
  display: flex;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  position: relative;
  z-index: 1;
}

.header-content {
  display: flex;
  align-items: center;
  height: 100%;
}

.app-title {
  font-size: 28px;
  font-weight: bold;
  display: flex;
  align-items: center;
  gap: 10px;
  color: #fff;
  margin: 0;
}
`;

// 粒子动画函数
const particleFunction = `
    // 粒子动画样式生成
    const getParticleStyle = () => {
      return {
        left: Math.random() * 100 + '%',
        animationDelay: Math.random() * 20 + 's',
        animationDuration: (Math.random() * 10 + 10) + 's',
        opacity: Math.random() * 0.6 + 0.2
      }
    }
`;

console.log('脚本内容已准备，请手动应用这些修改到Phase3和Phase4组件');
