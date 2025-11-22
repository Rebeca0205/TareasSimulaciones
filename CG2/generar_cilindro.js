import { V3 } from './3d-lib.js';
import fs from "fs";

function generateCylinderOBJ(sides, height, rBottom, rTop) {
  if (!Number.isInteger(sides) || sides < 3 || sides > 36) {
    throw new Error("sides debe ser un entero entre 3 y 36");
  }
  if (height <= 0 || rBottom <= 0 || rTop <= 0) {
    throw new Error("height, rBottom y rTop deben ser positivos");
  }

  const vertices = []; // [ [x,y,z], ... ]
  const faces = [];    // [ [a,b,c], ... ] índices 1-based

  // VÉRTICES (Y hacia arriba)
  // Anillo inferior: y = 0
  // Anillo superior: y = height

  // Anillo inferior 
  for (let i = 0; i < sides; i++) {
    const angle = (i / sides) * Math.PI * 2;
    const x = Math.cos(angle) * rBottom;
    const z = Math.sin(angle) * rBottom;
    vertices.push(V3.create(x, 0, z));
  }

  // Anillo superior
  for (let i = 0; i < sides; i++) {
    const angle = (i / sides) * Math.PI * 2;
    const x = Math.cos(angle) * rTop;
    const z = Math.sin(angle) * rTop;
    vertices.push(V3.create(x, height, z));
  }

  // Centros para tapas
  const centerBottomIndex = vertices.length + 1; // y = 0
  vertices.push(V3.create(0, 0, 0));

  const centerTopIndex = vertices.length + 1;    // y = height
  vertices.push(V3.create(0, height, 0));

  // CARAS LATERALES (TRIÁNGULOS, CCW (counter-clockwise), normales hacia afuera)
  //  Anillo inferior:  1 ... sides
  //  Anillo superior:  1+sides ... 2*sides
  //
  //  Para cada lado i:
  //    B0 = i
  //    B1 = next
  //    T0 = i + sides
  //    T1 = next + sides
  //
  //  Triángulos con normales hacia afuera (con producto cruz):
  //    (B0, T0, T1) y (B0, T1, B1)

  for (let i = 0; i < sides; i++) {
    const next = (i + 1) % sides; // conecta el último con el primero

    const B0 = i + 1;             // vértice base actual
    const B1 = next + 1;          // vértice base siguiente
    const T0 = i + 1 + sides;     // vértice top actual
    const T1 = next + 1 + sides;  // vértice top siguiente

    // Triángulo 1
    faces.push(V3.create(B0, T0, T1));
    // Triángulo 2
    faces.push(V3.create(B0, T1, B1));
  }


  // TAPA INFERIOR (y = 0, normal hacia abajo: (0, -1, 0))
  //
  //  Visto desde "abajo" (mirando hacia +Y desde y<0),
  //  las caras deben ser CCW. El orden correcto es:
  //    (centerBottom, Ri, Rnext)

  for (let i = 0; i < sides; i++) {
    const next = (i + 1) % sides;
    const Ri = i + 1;
    const Rnext = next + 1;
    faces.push(V3.create(centerBottomIndex, Ri, Rnext));
  }


  // TAPA SUPERIOR (y = height, normal hacia arriba: (0, +1, 0))
  //  Visto desde arriba (y>height mirando hacia abajo),
  //  las caras deben ser CCW. El orden correcto es:
  //    (centerTop, Rnext, Ri)
  //  donde Ri y Rnext son vértices del anillo superior.
 
  for (let i = 0; i < sides; i++) {
    const next = (i + 1) % sides;
    const Ri = i + 1 + sides;
    const Rnext = next + 1 + sides;
    faces.push(V3.create(centerTopIndex, Rnext, Ri));
  }

  // CÁLCULO DE NORMALES POR CARA (APUNTAN HACIA AFUERA)
  //    y escritura en formato OBJ:
  //    v  x y z
  //    vn nx ny nz
  //    f v1//n1 v2//n1 v3//n1

  function computeNormal(a, b, c) {
    // Vector AB = B - A
  const AB = V3.subtract(b, a);

  // Vector AC = C - A
  const AC = V3.subtract(c, a);

  // Producto cruzado AB x AC -> vector perpendicular
  const cross = V3.cross(AB, AC);

  // Normalizada para que tenga longitud 1
  const normal = V3.normalize(cross);

  return normal;
  }

  let obj = "";

  // Escribir vértices
  for (let i = 0; i < vertices.length; i++) {
    const v = vertices[i];
    obj += `v ${v[0]} ${v[1]} ${v[2]}\n`;
  }

  // Calcular normales (una por cara)
  const normals = [];
  for (let i = 0; i < faces.length; i++) {
    const f = faces[i];
    const a = vertices[f[0] - 1];
    const b = vertices[f[1] - 1];
    const c = vertices[f[2] - 1];
    normals.push(computeNormal(a, b, c));
  }

  //Escribir normales
  for (let i = 0; i < normals.length; i++) {
    const n = normals[i];
    obj += `vn ${n[0]} ${n[1]} ${n[2]}\n`;
  }

  // Caras: cada cara usa su propia normal (flat shading)
  // Índices de normales: 1..faces.length
  for (let i = 0; i < faces.length; i++) {
    const f = faces[i];
    const nIndex = i + 1;
    obj += `f ${f[0]}//${nIndex} ${f[1]}//${nIndex} ${f[2]}//${nIndex}\n`;
  }

  return obj;
}

let sides, height, rBottom, rTop;

const args = process.argv.slice(2);

if (args.length !== 4) {
  sides = 8;
  height = 6.0;
  rBottom = 1.0;
  rTop = 0.8;
} else {
  sides = parseInt(args[0]);
  height = parseFloat(args[1]);
  rBottom = parseFloat(args[2]);
  rTop = parseFloat(args[3]);
}

const filename = `cilindro_${sides}_${height}_${rBottom}_${rTop}.obj`;

console.log(`Generando modelo OBJ: ${filename} ...`);

try {
  const objText = generateCylinderOBJ(sides, height, rBottom, rTop);
  fs.writeFileSync(filename, objText, "utf8");
  console.log("Archivo generado correctamente:", filename);
} catch (error) {
  console.error("Error:", error.message);
}