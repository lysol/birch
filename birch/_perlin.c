#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <Python.h>
#include <structmember.h>
#include <stdio.h>
#include "_birch.h"

double randoms[RANDCOUNT];

void Perlin_dealloc(PerlinObject *self)
{
    Py_TYPE(self)->tp_free((PyObject *) self);
}

void shuffle(int *array, size_t n)
{
    if (n > 1) 
    {
        size_t i;
        for (i = 0; i < n - 1; i++) 
        {
          size_t j = i + rand() / (RAND_MAX / (n - i) + 1);
          int t = array[j];
          array[j] = array[i];
          array[i] = t;
        }
    }
}

PyObject *Perlin_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    PerlinObject *self;
    self = (PerlinObject *) type->tp_alloc(type, 0);
    for(int x=0; x<256; x++) {
        self->permutation[x] = x;
    }

    if (self != NULL) {
        self->seed = 200; //PyUnicode_FromString("");
    }
    return (PyObject *) self;
}

int Perlin_init(PerlinObject *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"seed", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|i", kwlist,
                                     &self->seed))
        return -1;
    srand(self->seed);
    shuffle(self->permutation, 256);
    for(int x=0; x<512; x++) {
        self->p[x] = self->permutation[x % 256];
    }
    // Hash lookup table as defined by Ken Perlin.  This is a randomly
    // arranged array of all numbers from 0-255 inclusive.
    for(int _z = 0; _z < RANDCOUNT; _z++) {
        randoms[_z] = (double)(rand() % 100) / 100;
    }

    return 0;
}

double fade(double t) {
    // Fade function as defined by Ken Perlin.  This eases coordinate values
    // so that they will "ease" towards integral values.  This ends up smoothing
    // the final output.
    return t * t * t * (t * (t * 6 - 15) + 10); // 6t^5 - 15t^4 + 10t^3
}

double grad(int hash, double x, double y, double z) {
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

double lerp(double start, double end, double x) {
    return start + x * (end - start);
}

int inc(int num) {
  num++;
  return num;
}

double perlin(int p[512], double x, double y, double z) {
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


double perlin_octave(int p[512], double x, double y, double z, double frequency,
        int octaves, double persistence) {
    double total = 0;
    double amplitude = .2;
    double maxValue = 0; // Used for normalizing result to 0.0 - 1.0
    for(int i=0;i<octaves;i++) {
        total += perlin(p, x * frequency, y * frequency, z * frequency) * amplitude;
        maxValue += amplitude;
        amplitude *= persistence;
        frequency *= 2;
    }
    return total/maxValue;
}

PyObject *Perlin_perlin_octave_array(PerlinObject *self, PyObject *args) {
    double x, y, width, height, frequency, persistence, step;
    int octaves;
    if (!PyArg_ParseTuple(args, "dddddidd", &x, &y, &width, &height,
                &frequency, &octaves, &persistence, &step)) {
        return NULL;
    }
    int row_count = floor(height / step);
    int col_count = floor(width / step);
    PyObject* row_list;
    PyObject* list = PyTuple_New(row_count);
    int a, b;
    double res;
    for (b=0; b<height / step; b++) {
        row_list = PyTuple_New(col_count);
        for (a=0; a<width / step; a++) {
            res = perlin_octave(self->p, (double)a*step+x, (double)b*step+y, 0, frequency, octaves, persistence);
            PyTuple_SetItem(row_list, a, PyFloat_FromDouble(res));
        }
        PyTuple_SetItem(list, b, row_list);
    }
    return list;
}

PyMemberDef Perlin_members[] = {
    {"seed", T_INT, offsetof(PerlinObject, seed), 0,
     "random seed"},
    {NULL}  /* Sentinel */ };

PyObject *Perlin_perlin(PerlinObject *self, PyObject *args) {
    double x, y;
    if (!PyArg_ParseTuple(args, "dd", &x, &y)) {
        return NULL;
    }
    return PyFloat_FromDouble(perlin(self->p, x, y, 0));
}

PyObject *Perlin_perlin_octave(PerlinObject *self, PyObject *args) {
    double x, y, frequency, persistence;
    int octaves;
    if (!PyArg_ParseTuple(args, "dddid", &x, &y, &frequency, &octaves, &persistence)) {
        return NULL;
    }
    return PyFloat_FromDouble(perlin_octave(self->p, x, y, 0, frequency, octaves, persistence));
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
            data[pix + 3] = (char)255;
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

PyObject *Perlin_noise2_bytes(PerlinObject *self, PyObject *args) {
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
            thresh = perlin_octave(self->p, rx, ry, 1.0, freq, octaves, 1.0);
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

PyMethodDef Perlin_methods[] = {
    {"noise2_bytes", (PyCFunction) Perlin_noise2_bytes, METH_VARARGS,
     "Perlin Noise 2D Array"
    },
    {"perlin_octave", (PyCFunction) Perlin_perlin_octave, METH_VARARGS,
        "Perlin Noise w/ octaves"},
    {"perlin_octave_array", (PyCFunction) Perlin_perlin_octave_array, METH_VARARGS,
        "Perlin Noise Array w/ octaves"},
    {"perlin", (PyCFunction) Perlin_perlin, METH_VARARGS,
        "Perlin Noise"},
    {NULL}  /* Sentinel */ };

PyTypeObject PerlinType = {
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
