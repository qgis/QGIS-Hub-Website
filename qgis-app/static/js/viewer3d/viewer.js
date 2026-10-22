import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {OBJLoader} from 'three/addons/loaders/OBJLoader.js';
import {MTLLoader} from 'three/addons/loaders/MTLLoader.js';
import {RoomEnvironment} from 'three/addons/environments/RoomEnvironment.js';

const CAMERA_START = new THREE.Vector3(0, 10, 20);

/**
 * Load a GLB file. A GLB carries its own materials and textures.
 */
async function loadGlb(url) {
  const gltf = await new GLTFLoader().loadAsync(url);
  return gltf.scene;
}

/**
 * Load an obj file with the mtl file that sits next to it. A model without a
 * readable mtl file still loads, it just arrives without its materials.
 */
async function loadObj(url, mtlUrl) {
  const objLoader = new OBJLoader();
  if (mtlUrl) {
    try {
      const materials = await new MTLLoader().loadAsync(mtlUrl);
      materials.preload();
      objLoader.setMaterials(materials);
    } catch (error) {
      console.error(error);
    }
  }
  return objLoader.loadAsync(url);
}

/**
 * The 3D viewer. Builds a scene for one model and exposes the actions the
 * control bar needs.
 */
export default class Viewer {
  constructor(canvas) {
    this.canvas = canvas;
    this.model = null;
    this.grid = null;
    this.wireframe = false;
    this.running = false;

    this.renderer = new THREE.WebGLRenderer({canvas, antialias: true});
    this.renderer.setPixelRatio(window.devicePixelRatio);
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;

    this.camera = new THREE.PerspectiveCamera(45, 2, 0.1, 1000);
    this.camera.position.copy(CAMERA_START);

    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color('white');
    this.scene.add(new THREE.HemisphereLight(0xb1e1ff, 0xb97a20, 1));

    this.controls = new OrbitControls(this.camera, canvas);
    this.controls.enableDamping = true;
    this.controls.autoRotateSpeed = 1.5;

    this.render = this.render.bind(this);
  }

  /**
   * Load the model and point the camera at it.
   */
  async load(format, url, mtlUrl) {
    if (format === 'glb') {
      // Materials in a GLB are physically based, so they need something to
      // reflect. Without this the model renders flat and grey.
      const environment = new THREE.PMREMGenerator(this.renderer);
      this.scene.environment = environment.fromScene(
        new RoomEnvironment(), 0.04
      ).texture;
      environment.dispose();
      this.model = await loadGlb(url);
    } else {
      this.model = await loadObj(url, mtlUrl);
    }
    this.scene.add(this.model);
    this.resetView();
    this.start();
    return this.model;
  }

  /**
   * Put the camera back where it started and frame the whole model.
   * Taken from https://discourse.threejs.org/t/camera-zoom-to-fit-object/936/21
   */
  resetView() {
    if (!this.model) {
      return;
    }
    this.resize();
    const box = new THREE.Box3().setFromObject(this.model);
    const center = box.getCenter(new THREE.Vector3());
    const size = box.getSize(new THREE.Vector3());

    const offset = 1.5;
    const fov = THREE.MathUtils.degToRad(this.camera.fov);
    const height = Math.max(size.y, size.x / this.camera.aspect, size.z);
    const distance = (height / 2 + offset) / Math.tan(fov / 2);

    const direction = CAMERA_START.clone().normalize();
    this.camera.position.copy(center).add(direction.multiplyScalar(distance));
    this.camera.near = Math.max(distance / 1000, 0.01);
    this.camera.far = distance * 100;
    this.camera.updateProjectionMatrix();

    // OrbitControls orbits around its target, so it has to know where the
    // model is. Without this the view swings around the scene origin.
    this.controls.target.copy(center);
    this.controls.update();
  }

  setWireframe(on) {
    this.wireframe = on;
    if (!this.model) {
      return;
    }
    this.model.traverse((child) => {
      const material = child.material;
      if (!material) {
        return;
      }
      const materials = Array.isArray(material) ? material : [material];
      materials.forEach((entry) => {
        if ('wireframe' in entry) {
          entry.wireframe = on;
        }
      });
    });
  }

  setGrid(on) {
    if (on && !this.grid && this.model) {
      const box = new THREE.Box3().setFromObject(this.model);
      const size = box.getSize(new THREE.Vector3());
      const span = Math.max(size.x, size.z, 1) * 2;
      this.grid = new THREE.GridHelper(span, 20, 0x999999, 0xdddddd);
      this.grid.position.y = box.min.y;
      this.scene.add(this.grid);
    }
    if (this.grid) {
      this.grid.visible = on;
    }
  }

  setAutoRotate(on) {
    this.controls.autoRotate = on;
  }

  /**
   * Match the drawing buffer to the size the canvas is shown at.
   */
  resize() {
    const width = this.canvas.clientWidth;
    const height = this.canvas.clientHeight;
    if (!width || !height) {
      return;
    }
    if (this.canvas.width !== width || this.canvas.height !== height) {
      this.renderer.setSize(width, height, false);
    }
    if (this.camera.aspect !== width / height) {
      this.camera.aspect = width / height;
      this.camera.updateProjectionMatrix();
    }
  }

  start() {
    if (!this.running) {
      this.running = true;
      requestAnimationFrame(this.render);
    }
  }

  render() {
    this.resize();
    this.controls.update();
    this.renderer.render(this.scene, this.camera);
    requestAnimationFrame(this.render);
  }
}
