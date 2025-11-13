/*
 * Script to draw a complex shape in 2D
 *
 * Gilberto Echeverria
 * 2024-07-12
 */


'use strict';

import * as twgl from 'twgl-base.js';
import { M3 } from './a01029805-2d-libs';
import GUI from 'lil-gui';

// Define the shader code, using GLSL 3.00

const vsGLSL = `#version 300 es
in vec2 a_position;

uniform vec2 u_resolution;
uniform mat3 u_transforms;

void main() {
    // Multiply the matrix by the vector, adding 1 to the vector to make
    // it the correct size. Then keep only the two first components
    vec2 position = (u_transforms * vec3(a_position, 1)).xy;

    // Convert the position from pixels to 0.0 - 1.0
    vec2 zeroToOne = position / u_resolution;

    // Convert from 0->1 to 0->2
    vec2 zeroToTwo = zeroToOne * 2.0;

    // Convert from 0->2 to -1->1 (clip space)
    vec2 clipSpace = zeroToTwo - 1.0;

    // Invert Y axis
    //gl_Position = vec4(clipSpace[0], clipSpace[1] * -1.0, 0, 1);
    gl_Position = vec4(clipSpace * vec2(1, -1), 0, 1);
}
`;

const fsGLSL = `#version 300 es
precision highp float;

uniform vec4 u_color;

out vec4 outColor;

void main() {
    outColor = u_color;
}
`;

function rectangle(x0, y0, x1, y1) {
  const arrays = {
    a_position: {
      numComponents: 2,
      data: [
        x0, y0,
        x1, y0,
        x1, y1,
        x0, y1,
      ]
    },
    indices: {
      numComponents: 3,
      data: [
        0, 1, 2,
        2, 3, 0
      ]
    }
  };
  return arrays;
}

function triangle(x0, y0, x1, y1, x2, y2) {
  const arrays = {
    a_position: {
      numComponents: 2,
      data: new Float32Array([
                x0,   y0,
                x1,  y1,
                x2,  y2,
            ])
    }
  };
  return arrays;
}

function circle(sides, radius = 50, cx, cy) {
  let arrays = {
    a_position: { numComponents: 2, data: [] },
    indices: { numComponents: 3, data: [] },
  };

  // Centro
  arrays.a_position.data.push(cx, cy);

  let angleStep = (2 * Math.PI) / sides;
  for (let s = 0; s < sides; s++) {
    let angle = angleStep * s;
    let x = cx + Math.cos(angle) * radius;
    let y = cy + Math.sin(angle) * radius;
    arrays.a_position.data.push(x, y);

    arrays.indices.data.push(0, s + 1, (s + 2) <= sides ? s + 2 : 1);
  }

  return arrays;
}


// Structure for the global data of all objects
// This data will be modified by the UI and used by the renderer
const objects = {
    Vox: {
      rectangle1: {
        transforms: {
            t: {
                x: 472.688,
                y: 232.128,
                z: 0,
            },
            rr: {
                x: 0,
                y: 0,
                z: 0,
            },
            s: {
                x: 0.6,
                y: 0.6,
                z: 1,
            }
        },
        vao: undefined,
        bufferInfo: undefined,
        arrays: undefined,
        color: [0, 0, 1, 1]
      },
      ojoIZQ: {
          transforms: {
              t: {
                  x: 472.688,
                  y: 232.128,
                  z: 0,
              },
              rr: {
                  x: 0,
                  y: 0,
                  z: 0,
              },
              s: {
                  x: 0.6,
                  y: 0.6,
                  z: 1,
              }
          },
          vao: undefined,
          bufferInfo: undefined,
          arrays: undefined,
          color: [1, 0, 0, 1]
      },
      ojoDER: {
          transforms: {
              t: {
                  x: 472.688,
                  y: 232.128,
                  z: 0,
              },
              rr: {
                  x: 0,
                  y: 0,
                  z: 0,
              },
              s: {
                  x: 0.6,
                  y: 0.6,
                  z: 1,
              }
          },
          vao: undefined,
          bufferInfo: undefined,
          arrays: undefined,
          color: [1, 0, 0, 1]
      },
      triangulo: {
          transforms: {
              t: {
                  x: 472.688,
                  y: 232.128,
                  z: 0,
              },
              rr: {
                  x: 0,
                  y: 0,
                  z: 0,
              },
              s: {
                  x: 0.6,
                  y: 0.6,
                  z: 1,
              }
          },
          vao: undefined,
          bufferInfo: undefined,
          arrays: undefined,
          color: [0, 1, 1, 1]
      },
      sombreroP1: {
          transforms: {
              t: {
                  x: 472.688,
                  y: 232.128,
                  z: 0,
              },
              rr: {
                  x: 0,
                  y: 0,
                  z: 0,
              },
              s: {
                  x: 0.6,
                  y: 0.6,
                  z: 1,
              }
          },
          vao: undefined,
          bufferInfo: undefined,
          arrays: undefined,
          color: [0, 0, 0, 1]
      },
      sombreroP2: {
          transforms: {
              t: {
                  x: 472.688,
                  y: 232.128,
                  z: 0,
              },
              rr: {
                  x: 0,
                  y: 0,
                  z: 0,
              },
              s: {
                  x: 0.6,
                  y: 0.6,
                  z: 1,
              }
          },
          vao: undefined,
          bufferInfo: undefined,
          arrays: undefined,
          color: [0, 0, 0, 1]
      },
    },

    Pivote:{
      transforms: {
              t: {
                  x: 472.688,
                  y: 232.128,
                  z: 0,
              },
              rr: {
                  x: 0,
                  y: 0,
                  z: 0,
              },
              s: {
                  x: 1,
                  y: 1,
                  z: 1,
              }
          },
      vao: undefined,
      bufferInfo: undefined,
      arrays: undefined,
      color: [1, 0, 0, 1]
    }
    
}

// Initialize the WebGL environmnet
function main() {
    const canvas = document.querySelector('canvas');
    const gl = canvas.getContext('webgl2');
    twgl.resizeCanvasToDisplaySize(gl.canvas);
    gl.viewport(0, 0, gl.canvas.width, gl.canvas.height);

    setupUI(gl);

    const programInfo = twgl.createProgramInfo(gl, [vsGLSL, fsGLSL]);

    //Rectangulo azul 380=x   
    objects.Vox.rectangle1.arrays = rectangle(-185, -150, 195, 100);
    objects.Vox.rectangle1.bufferInfo = twgl.createBufferInfoFromArrays(gl, objects.Vox.rectangle1.arrays);
    objects.Vox.rectangle1.vao = twgl.createVAOFromBufferInfo(gl, programInfo, objects.Vox.rectangle1.bufferInfo);

    //Ojos rojos
    objects.Vox.ojoIZQ.arrays = circle(50, 40, -55, -70);
    objects.Vox.ojoIZQ.bufferInfo = twgl.createBufferInfoFromArrays(gl, objects.Vox.ojoIZQ.arrays);
    objects.Vox.ojoIZQ.vao = twgl.createVAOFromBufferInfo(gl, programInfo, objects.Vox.ojoIZQ.bufferInfo);

    objects.Vox.ojoDER.arrays= circle(50, 40, 75, -70);
    objects.Vox.ojoDER.bufferInfo= twgl.createBufferInfoFromArrays(gl, objects.Vox.ojoDER.arrays);
    objects.Vox.ojoDER.vao = twgl.createVAOFromBufferInfo(gl, programInfo, objects.Vox.ojoDER.bufferInfo);

    //Sonrisa/Triangulo
    objects.Vox.triangulo.arrays = triangle(-155, 0, 10, 80, 165, 0);
    objects.Vox.triangulo.bufferInfo = twgl.createBufferInfoFromArrays(gl, objects.Vox.triangulo.arrays);
    objects.Vox.triangulo.vao = twgl.createVAOFromBufferInfo(gl, programInfo, objects.Vox.triangulo.bufferInfo);

    //Parte alta del sombrero
    objects.Vox.sombreroP1.arrays = rectangle(-35, -230, 50, -150);
    objects.Vox.sombreroP1.bufferInfo = twgl.createBufferInfoFromArrays(gl, objects.Vox.sombreroP1.arrays);
    objects.Vox.sombreroP1.vao = twgl.createVAOFromBufferInfo(gl, programInfo, objects.Vox.sombreroP1.bufferInfo);

    //Parte baja del sombrero
    objects.Vox.sombreroP2.arrays = rectangle(-55, -170, 70, -150);
    objects.Vox.sombreroP2.bufferInfo = twgl.createBufferInfoFromArrays(gl, objects.Vox.sombreroP2.arrays);
    objects.Vox.sombreroP2.vao = twgl.createVAOFromBufferInfo(gl, programInfo, objects.Vox.sombreroP2.bufferInfo);

    //Pivote
    objects.Pivote.arrays= circle(50, 20, 0, 0);
    objects.Pivote.bufferInfo= twgl.createBufferInfoFromArrays(gl, objects.Pivote.arrays);
    objects.Pivote.vao = twgl.createVAOFromBufferInfo(gl, programInfo, objects.Pivote.bufferInfo);
    drawScene(gl, programInfo, objects);

}

// Function to do the actual display of the objects
function drawScene(gl, programInfo, obj) {

  gl.useProgram(programInfo.program);

  let pivoteTra = M3.translation([obj.Pivote.transforms.t.x, obj.Pivote.transforms.t.y]);
  let pivoteminus = M3.translation([-obj.Pivote.transforms.t.x, -obj.Pivote.transforms.t.y]);

  for(const [modelName, model] of Object.entries(obj)){

    if (modelName === "Vox"){
      for (const [partName, part] of Object.entries(model)) {
      // Aseguramos que la parte tenga transformaciones (es dibujable)
      if (part.transforms) {
        let translate = [part.transforms.t.x, part.transforms.t.y];
        let angle_radians = part.transforms.rr.z;
        let scale = [part.transforms.s.x, part.transforms.s.y];

        // Create transform matrices
        let scaMat = M3.scale(scale);
        let rotMat = M3.rotation(angle_radians);
        let traMat = M3.translation(translate);

        // Create a composite matrix
        let transforms = M3.identity();
        transforms = M3.multiply(scaMat, transforms);
        transforms = M3.multiply(traMat, transforms);
        transforms = M3.multiply(pivoteminus, transforms);
        transforms = M3.multiply(rotMat, transforms);
        transforms = M3.multiply(pivoteTra, transforms);
        

        let uniforms =
        {
            u_resolution: [gl.canvas.width, gl.canvas.height],
            u_transforms: transforms,
            u_color: part.color,
        }

        twgl.setUniforms(programInfo, uniforms);

        gl.bindVertexArray(part.vao);

        twgl.drawBufferInfo(gl, part.bufferInfo);
      }

    }

    }

    if(modelName === "Pivote"){
      let translate = [model.transforms.t.x, model.transforms.t.y];
        let angle_radians = model.transforms.rr.z;
        let scale = [model.transforms.s.x, model.transforms.s.y];

        // Create transform matrices
        let scaMat = M3.scale(scale);
        let rotMat = M3.rotation(angle_radians);
        let traMat = M3.translation(translate);

        // Create a composite matrix
        let transforms = M3.identity();
        transforms = M3.multiply(scaMat, transforms);
        transforms = M3.multiply(rotMat, transforms);
        transforms = M3.multiply(traMat, transforms);

        let uniforms =
        {
            u_resolution: [gl.canvas.width, gl.canvas.height],
            u_transforms: transforms,
            u_color: model.color,
        }

        twgl.setUniforms(programInfo, uniforms);

        gl.bindVertexArray(model.vao);

        twgl.drawBufferInfo(gl, model.bufferInfo);
    }
  }
    
    requestAnimationFrame(() => drawScene(gl, programInfo, obj));
}

function setupUI(gl)
{
    const gui = new GUI();
    const voxFolder = gui.addFolder('Vox');

    const VtraFolder = voxFolder.addFolder('Translation');
    const VrotFolder = voxFolder.addFolder('Rotation');
    const VscaFolder = voxFolder.addFolder('Scale');

    VtraFolder.add(objects.Vox.rectangle1.transforms.t, 'x', 0, gl.canvas.width)
          .onChange(value => {
            objects.Vox.ojoIZQ.transforms.t.x = value,
            objects.Vox.ojoDER.transforms.t.x = value,
            objects.Vox.triangulo.transforms.t.x = value,
            objects.Vox.sombreroP1.transforms.t.x = value,
            objects.Vox.sombreroP2.transforms.t.x = value
          });

    VtraFolder.add(objects.Vox.rectangle1.transforms.t, 'y', 0, gl.canvas.height)
      .onChange(value => {
        objects.Vox.ojoIZQ.transforms.t.y = value,
        objects.Vox.ojoDER.transforms.t.y = value,
        objects.Vox.triangulo.transforms.t.y = value,
        objects.Vox.sombreroP1.transforms.t.y = value,
        objects.Vox.sombreroP2.transforms.t.y = value
      });
            
    VrotFolder.add(objects.Vox.rectangle1.transforms.rr, 'z', 0, Math.PI * 2)
      .onChange(value => {
        objects.Vox.ojoIZQ.transforms.rr.z = value,
        objects.Vox.ojoDER.transforms.rr.z = value,
        objects.Vox.triangulo.transforms.rr.z = value,
        objects.Vox.sombreroP1.transforms.rr.z = value,
        objects.Vox.sombreroP2.transforms.rr.z = value
      });
            
    VscaFolder.add(objects.Vox.rectangle1.transforms.s, 'x', -5, 5)
      .onChange(value => {
        objects.Vox.ojoIZQ.transforms.s.x = value,
        objects.Vox.ojoDER.transforms.s.x = value,
        objects.Vox.triangulo.transforms.s.x = value,
        objects.Vox.sombreroP1.transforms.s.x = value,
        objects.Vox.sombreroP2.transforms.s.x = value
      });

    VscaFolder.add(objects.Vox.rectangle1.transforms.s, 'y', -5, 5)
      .onChange(value => {
        objects.Vox.ojoIZQ.transforms.s.y = value,
        objects.Vox.ojoDER.transforms.s.y = value,
        objects.Vox.triangulo.transforms.s.y = value,
        objects.Vox.sombreroP1.transforms.s.y = value,
        objects.Vox.sombreroP2.transforms.s.y = value
      });

    const Pivote = gui.addFolder('Pivote');
    const PtraFolder = Pivote.addFolder('Translation');
    const ProtFolder = Pivote.addFolder('Rotation');
    const PscaFolder = Pivote.addFolder('Scale');

    PtraFolder.add(objects.Pivote.transforms.t, 'x', 0, gl.canvas.width);
    PtraFolder.add(objects.Pivote.transforms.t, 'y', 0, gl.canvas.height)
            
    ProtFolder.add(objects.Pivote.transforms.rr, 'z', 0, Math.PI * 2);
            
    PscaFolder.add(objects.Pivote.transforms.s, 'x', -5, 5);
    PscaFolder.add(objects.Pivote.transforms.s, 'y', -5, 5);
}

main()
