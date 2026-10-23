/**
 * Wire the viewer control bar. Every label lives in the template, so this
 * only moves state around.
 */

const fullscreenSupported = () =>
  Boolean(document.fullscreenEnabled || document.webkitFullscreenEnabled);

function setPressed(button, on) {
  button.setAttribute('aria-pressed', on ? 'true' : 'false');
  button.classList.toggle('is-active', on);
}

function requestFullscreen(element) {
  const request = element.requestFullscreen || element.webkitRequestFullscreen;
  if (request) {
    request.call(element);
  }
}

function exitFullscreen() {
  const exit = document.exitFullscreen || document.webkitExitFullscreen;
  if (exit) {
    exit.call(document);
  }
}

const isFullscreen = () =>
  Boolean(document.fullscreenElement || document.webkitFullscreenElement);

export default function bindControls(container, viewer) {
  const buttons = container.querySelectorAll('[data-viewer-action]');
  const toggles = {wireframe: false, grid: false, autorotate: false};

  const actions = {
    reset: () => viewer.resetView(),
    wireframe: (on) => viewer.setWireframe(on),
    grid: (on) => viewer.setGrid(on),
    autorotate: (on) => viewer.setAutoRotate(on),
    fullscreen: () => {
      if (isFullscreen()) {
        exitFullscreen();
      } else {
        requestFullscreen(container);
      }
    },
  };

  buttons.forEach((button) => {
    const action = button.dataset.viewerAction;
    if (action === 'fullscreen' && !fullscreenSupported()) {
      button.hidden = true;
      return;
    }
    button.addEventListener('click', () => {
      if (action in toggles) {
        toggles[action] = !toggles[action];
        setPressed(button, toggles[action]);
        actions[action](toggles[action]);
      } else {
        actions[action]();
      }
    });
  });

  const fullscreenButton = container.querySelector(
    '[data-viewer-action="fullscreen"]'
  );
  const onFullscreenChange = () => {
    const on = isFullscreen();
    container.classList.toggle('is-fullscreen', on);
    if (fullscreenButton) {
      setPressed(fullscreenButton, on);
    }
    // The canvas has a new size now, so frame the model again.
    viewer.resize();
  };
  document.addEventListener('fullscreenchange', onFullscreenChange);
  document.addEventListener('webkitfullscreenchange', onFullscreenChange);
  window.addEventListener('resize', () => viewer.resize());
}
