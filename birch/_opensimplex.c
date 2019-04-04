#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include </usr/include/python3.6m/Python.h>
#include </usr/include/python3.6m/structmember.h>
#include </usr/lib/python3/dist-packages/numpy/core/include/numpy/arrayobject.h>
#include "open_simplex.h"
#include <stdio.h>
#define OCTAVES 3
#define FEATURE_SIZE 24.0

typedef struct {
    PyObject_HEAD
    int seed; /* random seed */
    struct osn_context *ctx;
} OpenSimplexObject;

static void OpenSimplex_dealloc(OpenSimplexObject *self)
{
    Py_XDECREF(self->ctx);
    Py_TYPE(self)->tp_free((PyObject *) self);
}

static PyObject *OpenSimplex_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    OpenSimplexObject *self;
    self = (OpenSimplexObject *) type->tp_alloc(type, 0);
    if (self != NULL) {
        self->seed = 200; //PyUnicode_FromString("");
    }
    return (PyObject *) self;
}

static int OpenSimplex_init(OpenSimplexObject *self, PyObject *args, PyObject *kwds)
{
    static char *kwlist[] = {"seed", NULL};

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "|i", kwlist,
                                     &self->seed))
        return -1;
    printf("seed: %d\n", self->seed);
    open_simplex_noise(self->seed, &self->ctx);
    Py_INCREF(self->ctx);

    return 0;
}

static PyMemberDef OpenSimplex_members[] = {
    {"seed", T_INT, offsetof(OpenSimplexObject, seed), 0,
     "random seed"},
    {"ctx", T_NONE, offsetof(OpenSimplexObject, ctx), RESTRICTED,
        "opensimplex context"},
    {NULL}  /* Sentinel */ };

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

static PyObject *OpenSimplex_noise2_array(OpenSimplexObject *self, PyObject *args) {
    int x;
    int y;
    double freq;
    int size;
    if (!PyArg_ParseTuple(args, "iidi", &x, &y, &freq, &size))
        return NULL;
    int total = size * size * 4;
    char *data = malloc(total);
    char pix;
    int idx, ry, rx, a, b, row_offset, col_offset;
    freq = freq / 24.0;
    for(b = 0; b < size; b++) {
        for(a = 0; a < size; a++) {
            row_offset = b * size * 4;
            col_offset = a * 4;
            idx = row_offset + col_offset;
            ry = y + b;
            rx = x + a;
            double thresh = 0;
            double v0, v1, v2;

            /* Use three octaves: frequency N, N/2 and N/4 with relative amplitudes 4:2:1. */
            v0 = open_simplex_noise4(self->ctx, (double) rx / FEATURE_SIZE / 4,
                  (double) ry / FEATURE_SIZE / 4, 0.0, 0.0);
            v1 = open_simplex_noise4(self->ctx, (double) rx / FEATURE_SIZE / 2,
                  (double) ry / FEATURE_SIZE / 2, 0.0, 0.0);
            v2 = open_simplex_noise4(self->ctx, (double) rx / FEATURE_SIZE / 1,
                  (double) ry / FEATURE_SIZE / 1, 0.0, 0.0);
            thresh = v0 * 4 / 7.0 + v1 * 2 / 7.0 + v2 * 1 / 7.0;

            pix = (uint8_t) ((thresh + 1) * 127.5);
            pix = 0x0ff << 24 | pix;

            data[idx] = pix;
            data[idx + 1] = pix;
            data[idx + 2] = pix;
            data[idx + 3] = 255;
        }
    }
    dither_buffer(data, total, size * 4);
    const char *derp = data;
    PyObject *array = PyBytes_FromStringAndSize(derp, total);
    free(data);
    return array;
}


static PyObject *OpenSimplex_noise2(OpenSimplexObject *self, PyObject *args) {
    double x;
    double y;
    double res;
    if (!PyArg_ParseTuple(args, "dd", &x, &y))
        return NULL;
    res = open_simplex_noise2(self->ctx, x, y);
    return PyFloat_FromDouble(res);
}

static PyMethodDef OpenSimplex_methods[] = {
    {"noise2", (PyCFunction) OpenSimplex_noise2, METH_VARARGS,
     "OpenSimplex Noise 2D"
    },
    {"noise2_array", (PyCFunction) OpenSimplex_noise2_array, METH_VARARGS,
     "OpenSimplex Noise 2D Array"
    },
    {NULL}  /* Sentinel */ };

static PyTypeObject OpenSimplexType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "open_simplex.OpenSimplex",
    .tp_doc = "A python wrapper for opensimplex c code",
    .tp_basicsize = sizeof(OpenSimplexObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_new = OpenSimplex_new,
    .tp_init = (initproc) OpenSimplex_init,
    .tp_dealloc = (destructor) OpenSimplex_dealloc,
    .tp_members = OpenSimplex_members,
    .tp_methods = OpenSimplex_methods,
};

static PyModuleDef opensimplex_module = {
    PyModuleDef_HEAD_INIT,
    .m_name = "open_simplex",
    .m_doc = "A python wrapper for opensimplex c code.",
    .m_size = -1,
};

PyMODINIT_FUNC PyInit_open_simplex(void)
{
    PyObject *m;
    if (PyType_Ready(&OpenSimplexType) < 0)
        return NULL;

    m = PyModule_Create(&opensimplex_module);
    if (m == NULL)
        return NULL;

    Py_INCREF(&OpenSimplexType);
    PyModule_AddObject(m, "OpenSimplex", (PyObject *) &OpenSimplexType);
    return m;
}

