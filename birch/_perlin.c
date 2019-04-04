#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include </usr/include/python3.6m/Python.h>
#include </usr/include/python3.6m/structmember.h>
#include </usr/lib/python3/dist-packages/numpy/core/include/numpy/arrayobject.h>
#include <stdio.h>
#define RANDCOUNT (1024 * 1024)
#define GOOSE .4
#define GANDER 0.01

typedef struct {
    PyObject_HEAD
    int seed; /* random seed */
    int permutation[512];
    int p[512];
} PerlinObject;

static int permutation[512] = { 151,160,137,91,90,15,
        131,13,201,95,96,53,194,233,7,225,140,36,103,30,69,142,8,99,37,240,21,10,23,
        190, 6,148,247,120,234,75,0,26,197,62,94,252,219,203,117,35,11,32,57,177,33,
        88,237,149,56,87,174,20,125,136,171,168, 68,175,74,165,71,134,139,48,27,166,
        77,146,158,231,83,111,229,122,60,211,133,230,220,105,92,41,55,46,245,40,244,
        102,143,54, 65,25,63,161, 1,216,80,73,209,76,132,187,208, 89,18,169,200,196,
        135,130,116,188,159,86,164,100,109,198,173,186, 3,64,52,217,226,250,124,123,
        5,202,38,147,118,126,255,82,85,212,207,206,59,227,47,16,58,17,182,189,28,42,
        223,183,170,213,119,248,152, 2,44,154,163, 70,221,153,101,155,167, 43,172,9,
        129,22,39,253, 19,98,108,110,79,113,224,232,178,185, 112,104,218,246,97,228,
        251,34,242,193,238,210,144,12,191,179,162,241, 81,51,145,235,249,14,239,107,
        49,192,214, 31,181,199,106,157,184, 84,204,176,115,121,50,45,127, 4,150,254,
        138,236,205,93,222,114,67,29,24,72,243,141,128,195,78,66,215,61,156,180
      };
static int p[512];

static double randoms[RANDCOUNT];

static void Perlin_dealloc(PerlinObject *self)
{
    Py_TYPE(self)->tp_free((PyObject *) self);
}

static PyObject *Perlin_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PerlinObject *self;
    self = (PerlinObject *) type->tp_alloc(type, 0);
    for(int x=0; x<512; x++) {
        p[x] = permutation[x % 256];
    }
    if (self != NULL) {
        self->seed = 200; //PyUnicode_FromString("");
    }
    return (PyObject *) self;
}

static int Perlin_init(PerlinObject *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"seed", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|i", kwlist,
                                     &self->seed))
        return -1;
    printf("seed: %d\n", self->seed);
    // Hash lookup table as defined by Ken Perlin.  This is a randomly
    // arranged array of all numbers from 0-255 inclusive.
    for(int _z = 0; _z < RANDCOUNT; _z++) {
        randoms[_z] = (double)(rand() % 100) / 100;
    }

    return 0;
}

static double fade(double t) {
    // Fade function as defined by Ken Perlin.  This eases coordinate values
    // so that they will "ease" towards integral values.  This ends up smoothing
    // the final output.
    return t * t * t * (t * (t * 6 - 15) + 10); // 6t^5 - 15t^4 + 10t^3
}

static double grad(int hash, double x, double y, double z) {
    int h = hash & 15;                  // Take the hashed value and take the first 4 bits of it (15 == 0b1111)
    double u = h < 8 /* 0b1000 */ ? x : y;        // If the most significant bit (MSB) of the hash is 0 then set u = x.  Otherwise y.
    double v;                      // In Ken Perlin's original implementation this was another conditional operator (?:).  I
                              // expanded it for readability.
    if(h < 4 /* 0b0100 */)                // If the first and second significant bits are 0 set v = y
        v = y;
    else if(h == 12 /* 0b1100 */ || h == 14 /* 0b1110*/)// If the first and second significant bits are 1 set v = x
        v = x;
    else                         // If the first and second significant bits are not equal (0/1, 1/0) set v = z
        v = z;
    return ((h&1) == 0 ? u : -u)+((h&2) == 0 ? v : -v);
    // Use the last 2 bits to decide if u and v are positive or negative.  Then return their addition.
}

static double lerp(double start, double end, double x) {
    return start + x * (end - start);
}

int inc(int num) {
  num++;
  return num;
}

static double perlin(double x, double y, double z) {
    int xi = (int)floor(x) & 255;
    int yi = (int)floor(y) & 255;
    int zi = (int)floor(z) & 255;
    double xf = x-floor(x);
    double yf = y-floor(y);
    double zf = z-floor(z);
    double u = fade(xf);
    double v = fade(yf);
    double w = fade(zf);
    int aaa, aba, aab, abb, baa, bba, bab, bbb;
    aaa = p[p[p[    xi ]+    yi ]+    zi ];
    aba = p[p[p[    xi ]+inc(yi)]+    zi ];
    aab = p[p[p[    xi ]+    yi ]+inc(zi)];
    abb = p[p[p[    xi ]+inc(yi)]+inc(zi)];
    baa = p[p[p[inc(xi)]+    yi ]+    zi ];
    bba = p[p[p[inc(xi)]+inc(yi)]+    zi ];
    bab = p[p[p[inc(xi)]+    yi ]+inc(zi)];
    bbb = p[p[p[inc(xi)]+inc(yi)]+inc(zi)];
    double x1, x2, y1, y2;

    x1 = lerp(grad(aaa, xf, yf, zf),
                    grad (baa, xf-1, yf  , zf),
                    u);
    x2 = lerp(    grad (aba, xf  , yf-1, zf),
                grad (bba, xf-1, yf-1, zf),
                  u);
    y1 = lerp(x1, x2, v);

    x1 = lerp(    grad (aab, xf  , yf  , zf-1),
                grad (bab, xf-1, yf  , zf-1),
                u);
    x2 = lerp(    grad (abb, xf  , yf-1, zf-1),
                  grad (bbb, xf-1, yf-1, zf-1),
                  u);
    y2 = lerp (x1, x2, v);
    return (lerp (y1, y2, w)+1)/2;
}

static double perlin_octave(double x, double y, double z, double frequency,
        int octaves, double persistence) {
    double total = 0;
    double amplitude = .2;
    double maxValue = 0; // Used for normalizing result to 0.0 - 1.0
    for(int i=0;i<octaves;i++) {
        total += perlin(x * frequency, y * frequency, z * frequency) * amplitude;
        maxValue += amplitude;
        amplitude *= persistence;
        frequency *= 2;
    }
    return total/maxValue;
}

static PyMemberDef Perlin_members[] = {
    {"seed", T_INT, offsetof(PerlinObject, seed), 0,
     "random seed"},
    {NULL}  /* Sentinel */ };

static PyObject *Perlin_perlin(PerlinObject *self, PyObject *args) {
    double x, y;
    if (!PyArg_ParseTuple(args, "dd", &x, &y)) {
        return NULL;
    }
    return PyFloat_FromDouble(perlin(x, y, 0));
}

static PyObject *Perlin_perlin_octave(PerlinObject *self, PyObject *args) {
    double x, y, frequency, persistence;
    int octaves;
    if (!PyArg_ParseTuple(args, "dddid", &x, &y, &frequency, &octaves, &persistence)) {
        return NULL;
    }
    return PyFloat_FromDouble(perlin_octave(x, y, 0, frequency, octaves, persistence));
}

void dither_buffer(char *data, int size, int stride) {
    /*
     for each y from top to bottom
   for each x from left to right
      oldpixel := pixel[x][y]
      newpixel := find_closest_palette_color(oldpixel)
      pixel[x][y] := newpixel
      quant_error := oldpixel - newpixel
      pixel[x+1][y] := pixel[x+1][y] + 7/16 * quant_error
      pixel[x-1][y+1] := pixel[x-1][y+1] + 3/16 * quant_error
      pixel[x][y+1] := pixel[x][y+1] + 5/16 * quant_error
      pixel[x+1][y+1] := pixel[x+1][y+1] + 1/16 * quant_error
      */
    int rows = size / stride;
    uint8_t old, new;
    double error;
    int offset;
    int pix, one_right, one_left, one_down, one_down_right;
    double sev = 7.0/16.0,
           thr = 3.0/16.0,
           fiv = 5.0/16.0,
           one = 1.0/16.0;
    uint8_t flutter = 48;
    for(int y = 0; y < rows; y++) {
        for (int x = 0; x < stride; x += 4) {
            offset = y * stride + x;
            pix = offset;
            one_right = offset + 4;
            one_left = offset - 4;
            one_down = offset + stride;
            one_down_right = offset + stride + 4;
            int r = rand() % flutter + (flutter / 2);
            old = (uint8_t)data[pix];
            if ((r > 0 && old < 255 - r) || (r < 0 && old > r)) {
                old = old + r;
            }
            new = old > 127 ? 255 : (255 - 64);
            if (x + y % 4 != 0) {
                new = 255;
            }
            data[pix] = new;
            data[pix + 1] = new;
            data[pix + 2] = new;
            data[pix + 3] = 255;
            error = (double)old - (double)new;
            if (x != stride - 1) {
                data[one_right]      = (uint8_t)data[one_right]      + (int)(sev * error);
                data[one_right + 1]      = (uint8_t)data[one_right + 1]      + (int)(sev * error);
                data[one_right + 2]      = (uint8_t)data[one_right + 2]      + (int)(sev * error);
            }
            if (x > 0) {
                data[one_left]       = (uint8_t)data[one_left]       + (int)(thr * error);
                data[one_left + 1]       = (uint8_t)data[one_left + 1]       + (int)(thr * error);
                data[one_left + 2]       = (uint8_t)data[one_left + 2]       + (int)(thr * error);
            }
            if (x != stride - 1 && y != rows - 1) {
                data[one_down_right] = (uint8_t)data[one_down_right] + (int)(one * error);
                data[one_down_right + 1] = (uint8_t)data[one_down_right + 1] + (int)(one * error);
                data[one_down_right + 2] = (uint8_t)data[one_down_right + 2] + (int)(one * error);
            }
            if (y != rows - 1) {
                data[one_down]       = (uint8_t)data[one_down]       + (int)(fiv * error);
                data[one_down + 1]       = (uint8_t)data[one_down]       + (int)(fiv * error);
                data[one_down + 2]       = (uint8_t)data[one_down]       + (int)(fiv * error);
            }
            if (x == 0 && y == 0) {
                printf("old %d new %d error %2.f\n", old, new, error);
            }
        }
    }
}

static PyObject *Perlin_noise2_bytes(PerlinObject *self, PyObject *args) {
    int x;
    int y;
    double freq;
    int size;
    int octaves;
    int pixvalue;
    if (!PyArg_ParseTuple(args, "iidiii", &x, &y, &freq, &octaves, &size, &pixvalue))
        return NULL;
    int total = size * size * 4;
    char *data = malloc(total);
    char pix;
    int idx, a, b, row_offset, col_offset, ridx, ridx2;
    double rx, ry;
    double thresh, ranz, repz;
    for(b = 0; b < size; b++) {
        for(a = 0; a < size; a++) {
            row_offset = b * size * 4;
            col_offset = a * 4;
            idx = row_offset + col_offset;
            ry = (y + b);
            rx = (x + a);
            thresh = perlin_octave(rx, ry, 1.0, freq, octaves, 1.0);
            // noise2(rx, ry ...)
            ridx = idx % RANDCOUNT;
            ridx2 = (idx + 666) % RANDCOUNT;
            ranz = randoms[ridx];
            repz = randoms[ridx2];
            pix = pixvalue;
            if (ranz < GANDER) {
                pix = 0;
            } else if (repz < thresh - GOOSE) {
                pix = 0;
            }

            data[idx] = pix;
            data[idx + 1] = pix;
            data[idx + 2] = pix;
            data[idx + 3] = pix ^ pixvalue;
        }
    }
    //dither_buffer(data, total, size * 4);
    const char *derp = data;
    PyObject *array = PyBytes_FromStringAndSize(derp, total);
    free(data);
    return array;
}

static PyMethodDef Perlin_methods[] = {
    {"noise2_bytes", (PyCFunction) Perlin_noise2_bytes, METH_VARARGS,
     "Perlin Noise 2D Array"
    },
    {"perlin_octave", (PyCFunction) Perlin_perlin_octave, METH_VARARGS,
        "Perlin Noise w/ octaves"},
    {"perlin", (PyCFunction) Perlin_perlin, METH_VARARGS,
        "Perlin Noise"},
    {NULL}  /* Sentinel */ };

static PyTypeObject PerlinType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "perlin.Perlin",
    .tp_doc = "A python wrapper for perlin noise c code",
    .tp_basicsize = sizeof(PerlinObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_new = Perlin_new,
    .tp_init = (initproc) Perlin_init,
    .tp_dealloc = (destructor) Perlin_dealloc,
    .tp_members = Perlin_members,
    .tp_methods = Perlin_methods,
};

static PyModuleDef perlin_module = {
    PyModuleDef_HEAD_INIT,
    .m_name = "perlin",
    .m_doc = "A python wrapper for perlin noise c code.",
    .m_size = -1,
};

PyMODINIT_FUNC PyInit__perlin(void)
{
    PyObject *m;
    if (PyType_Ready(&PerlinType) < 0)
        return NULL;

    m = PyModule_Create(&perlin_module);
    if (m == NULL)
        return NULL;

    Py_INCREF(&PerlinType);
    PyModule_AddObject(m, "Perlin", (PyObject *) &PerlinType);
    return m;
}

