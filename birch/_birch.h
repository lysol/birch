#ifndef BIRCH_H
#define BIRCH_H
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include </usr/include/python3.6m/Python.h>
#include </usr/include/python3.6m/structmember.h>

// perlin stuff

#define RANDCOUNT (1024 * 1024)
#define GOOSE .4
#define GANDER 0.01

typedef struct {
    PyObject_HEAD
    unsigned int seed; /* random seed */
    int permutation[512];
    int p[512];
} PerlinObject;
double randoms[RANDCOUNT];

void Perlin_dealloc(PerlinObject *self);
void shuffle(int *array, size_t n);
PyObject *Perlin_new(PyTypeObject *type, PyObject *args, PyObject *kwds);
int Perlin_init(PerlinObject *self, PyObject *args, PyObject *kwds);
double fade(double t);
double grad(int hash, double x, double y, double z);
double lerp(double start, double end, double x);
int inc(int num);
double perlin(int p[512], double x, double y, double z);
double perlin_octave(int p[512], double x, double y, double z, double frequency,
        int octaves, double persistence);
PyObject *Perlin_perlin_octave_array(PerlinObject *self, PyObject *args);
PyObject *Perlin_perlin(PerlinObject *self, PyObject *args);
PyObject *Perlin_perlin_octave(PerlinObject *self, PyObject *args);
void dither_buffer(char *data, int size, int stride);
PyObject *Perlin_noise2_bytes(PerlinObject *self, PyObject *args);
PyTypeObject PerlinType;

// Rect stuff

#define collidepoint(rect, x, y) (x >= rect->x && x < rect->x + rect->width && \
        y >= rect->y && y < rect->y + rect->height)

#define colliderect(first, second) ( \
        !((second->x + second->width - 1) < first->x || second->x > (first->x + first->width - 1) || \
        (second->y + second->height - 1) < first->y || second->y > (first->y + first->height - 1)) \
        )

typedef struct {
    PyObject_HEAD
    int x;
    int y;
    int width;
    int height;
} RectObject;

typedef struct {
    int x;
    int y;
    int width;
    int height;
} RectShallow;

PyTypeObject RectType;
void Rect_dealloc(RectObject *self);
PyObject *Rect_new(PyTypeObject *type, PyObject *args, PyObject *kwds);
int Rect_init(RectObject *self, PyObject *args, PyObject *kwds);
PyObject *Rect___str__(RectObject *self);
PyObject *Rect_inflate(RectObject *self, PyObject *args);
PyObject *Rect_collidepoint(RectObject *self, PyObject *args);
PyObject *Rect_colliderect(RectObject *self, PyObject *args);
PyObject* Rect_get_right(RectObject* self, void* closure);
int Rect_set_right(RectObject* self, PyObject* value, void* closure);
PyObject* Rect_get_bottom(RectObject* self, void* closure);
int Rect_set_bottom(RectObject* self, PyObject* value, void* closure);
PyObject* Rect_get_center(RectObject* self, void* closure);
int Rect_set_center(RectObject* self, PyObject* value, void* closure);
PyObject* Rect_get_position(RectObject* self, void* closure);
int Rect_set_position(RectObject* self, PyObject* value, void* closure);
PyObject* Rect_get_topright(RectObject* self, void* closure);
int Rect_set_topright(RectObject* self, PyObject* value, void* closure);
PyObject* Rect_get_bottomleft(RectObject* self, void* closure);
int Rect_set_bottomleft(RectObject* self, PyObject* value, void* closure);
PyObject* Rect_get_bottomright(RectObject* self, void* closure);
int Rect_set_bottomright(RectObject* self, PyObject* value, void* closure);
PyTypeObject RectType;


// World stuff

typedef struct {
    PyObject_HEAD
    int chunk_size;
    PyObject *world;
    PyObject *world_meta;
    PyObject *seeded;
    PyObject *batches;
    PyObject *vertex_lists;
    PyObject *bg_batches;
    PyObject *bgs;
} WorldObject;

// module
PyObject *_module;
PyObject *graphics;
PyObject *Batch;
PyObject *draw;

PyTypeObject WorldType;
void World_dealloc(WorldObject *self);
PyObject *World_new(PyTypeObject *type, PyObject *args, PyObject *kwds);
int World_init(WorldObject *self, PyObject *args, PyObject *kwds);
PyTypeObject WorldType;

void insert(WorldObject *self, int ox, int oy, PyObject *sprite);
void delete(WorldObject *self, int ox, int oy, PyObject *sprite);

#endif
