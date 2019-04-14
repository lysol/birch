#include </usr/include/python3.6m/Python.h>
#include </usr/include/python3.6m/structmember.h>
#include <stdio.h>
#include "_world.h"

static void World_dealloc(WorldObject *self)
{
    Py_TYPE(self)->tp_free((PyObject *) self);
}

static PyObject *World_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    WorldObject *self;
    self = (WorldObject *) type->tp_alloc(type, 0);
    return (PyObject *) self;
}

static int World_init(WorldObject *self, PyObject *args, PyObject *kwds)
{
    self->world = PyDict_New();
    self->seeded = PyDict_New();
    self->batches = PyDict_New();
    self->vertex_lists = PyDict_New();
    self->bg_batches = PyDict_New();
    self->bgs = PyDict_New();
    self->chunk_size = 1024;
    return 0;
}

static int *alias(int *ox, int *oy, int chunk_size, int x, int y) {
    *ox = (x - x % chunk_size) / chunk_size;
    *oy = (y - y % chunk_size) / chunk_size;
    return 0;
}

static PyObject *World__alias(WorldObject *self, PyObject *args) {
    int x, y;
    if (!PyArg_ParseTuple(args, "ii", &x, &y)) {
        return NULL;
    }
    int ox, oy;
    alias(&ox, &oy, self->chunk_size, x, y);
    return Py_BuildValue("ii",
        ox,
        oy
        );
}

static PyObject *World_unseeded(WorldObject *self, PyObject *args) {
    int x, y;
    if (!PyArg_ParseTuple(args, "ii", &x, &y)) {
        return NULL;
    }
    int ox, oy;
    alias(&ox, &oy, self->chunk_size, x, y);
    PyObject *key = Py_BuildValue("ii", ox, oy);
    if (PyDict_Contains(self->seeded, key)) {
        Py_DECREF(key);
        Py_RETURN_FALSE;
    } else {
        Py_DECREF(key);
        Py_RETURN_TRUE;
    }
}

static PyObject *World__inflate(WorldObject *self, PyObject *args, PyObject *kwargs) {
    int ix, iy, priority = 10;
    static char *keywords[] = {"ix", "iy", "priority", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "ii|i", keywords, &ix, &iy, &priority)) {
        return NULL;
    }
    int changed = 0;
    PyObject *pix = PyLong_FromLong(ix);
    PyObject *piy = PyLong_FromLong(iy);
    PyObject *key = Py_BuildValue("ii", ix, iy);
    PyObject *rdict, *cdict;
    if (!PyDict_Contains(self->world, piy)) {
        rdict = PyDict_New();
        PyDict_SetItem(self->world, piy, rdict);
        changed = 1;
    } else {
        rdict = PyDict_GetItem(self->world, piy);
    }
    if (!PyDict_Contains(rdict, pix)) {
        cdict = PyDict_New();
        PyDict_SetItem(rdict, pix, cdict);
        changed = 1;
    } else {
        cdict = PyDict_GetItem(rdict, pix);
    }
    if (changed) {
        PyObject *batch = PyDict_New();
        PyObject *pgbatch = PyObject_CallObject(Batch, NULL);
        PyDict_SetItem(self->batches, key, batch);
        PyObject *ppri = PyLong_FromLong(priority);
        PyDict_SetItem(batch, ppri, pgbatch);
        Py_DECREF(ppri);
    }
    Py_DECREF(pix);
    Py_DECREF(piy);
    Py_DECREF(key);
    return Py_None;
}

static PyObject *World_set_bg(WorldObject *self, PyObject *args) {
    PyObject *sprite;
    int x, y;
    if (!PyArg_ParseTuple(args, "Oii", &sprite, &x, &y)) {
        return NULL;
    }
    int ox, oy;
    alias(&ox, &oy, self->chunk_size, x, y);
    PyObject *key = Py_BuildValue("ii", ox, oy);
    PyObject *pgbatch;
    if (!PyDict_Contains(self->bg_batches, key)) {
        pgbatch = PyObject_CallObject(Batch, NULL);
        PyDict_SetItem(self->bg_batches, key, pgbatch);
    } else {
        pgbatch = PyDict_GetItem(self->bg_batches, key);
    }
    PyObject_SetAttrString(sprite, "batch", pgbatch);
    char bgs_key[30] = "";
    sprintf(bgs_key, "%d_%d", ox, oy);
    PyDict_SetItemString(self->bgs, bgs_key, sprite);
    Py_DECREF(key);
    return Py_None;
}

static PyObject *get_cell(WorldObject *self, int ox, int oy) {
    PyObject *row = PyDict_GetItem(self->world, PyLong_FromLong(oy));
    PyObject *cell = PyDict_GetItem(row, PyLong_FromLong(ox));
    return cell;
}

static PyObject *World_insert(WorldObject *self, PyObject *args) {
    PyObject *sprite;
    int x, y;
    if (!PyArg_ParseTuple(args, "Oii", &sprite, &x, &y)) {
        return NULL;
    }
    int ox, oy;
    alias(&ox, &oy, self->chunk_size, x, y);
    PyObject *key = Py_BuildValue("ii", ox, oy);
    PyObject *pgbatch;
    PyObject *kwargs = PyDict_New();
    PyObject *priority = PyObject_GetAttrString(sprite, "priority");
    PyDict_SetItemString(kwargs, "priority", priority);
    World__inflate(self, key, kwargs);
    PyObject *chunk_batch_dict = PyDict_GetItem(self->batches, key);
    if (!PyDict_Contains(chunk_batch_dict, priority)) {
        pgbatch = PyObject_CallObject(Batch, NULL);
        PyDict_SetItem(chunk_batch_dict, key, pgbatch);
    } else {
        pgbatch = PyDict_GetItem(chunk_batch_dict, priority);
    }
    PyObject *cell = get_cell(self, ox, oy);
    PyDict_SetItem(cell, PyObject_GetAttrString(sprite, "id"), sprite);
    Py_DECREF(key);
    Py_DECREF(kwargs);
    Py_DECREF(priority);
    return Py_None;
}

static PyObject *World_delete(WorldObject *self, PyObject *args) {
    PyObject *sprite;
    int x, y;
    if (!PyArg_ParseTuple(args, "Oii", &sprite, &x, &y)) {
        return NULL;
    }
    int ox, oy;
    alias(&ox, &oy, self->chunk_size, x, y);
    PyObject *key = Py_BuildValue("ii", ox, oy);
    World__inflate(self, key, NULL);
    PyObject_SetAttrString(sprite, "batch", Py_None);
    PyObject *cell = get_cell(self, ox, oy);

    PyObject *spriteId = PyObject_GetAttrString(sprite, "id");
    PyDict_DelItem(cell, spriteId);
    Py_DECREF(spriteId);

    Py_DECREF(key);
    return Py_None;
}

static PyObject *World_get(WorldObject *self, PyObject *args) {
    int x, y, w, h;
    if (!PyArg_ParseTuple(args, "iiii", &x, &y, &w, &h)) {
        return NULL;
    }
    int ox, oy, px, py;
    alias(&ox, &oy, self->chunk_size, x, y);
    alias(&px, &py, self->chunk_size, x + w, y + h);
    PyObject *out = PyList_New(0);
    for(int yes=oy; yes<py+1; yes++) {
        for(int xes=ox; xes<px+1; xes++) {
            PyObject *key = Py_BuildValue("ii", xes, yes);
            World__inflate(self, key, NULL);
            PyObject *cell = get_cell(self, xes, yes);
            PyObject *cellVals = PyDict_Values(cell);
            PyObject *iterator = PyObject_GetIter(cellVals);
            PyObject *item;

            if (iterator == NULL) {
                continue;
            }

            while (item = PyIter_Next(iterator)) {
                // do the stuff here
                PyList_Append(out, item);
                Py_DECREF(item);
            }

            Py_DECREF(iterator);
            Py_DECREF(cellVals);
            Py_DECREF(key);

            if (PyErr_Occurred()) {
                return NULL;
            }

        }
    }
    return out;
}

static PyObject *World_get_chunks(WorldObject *self, PyObject *args, PyObject *kwargs) {
    int x, y, w = 1, h = 1;
    static char *keywords[] = {"x", "y", "w", "h", NULL};
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "ii|Ii", keywords, &x, &y, &w, &h)) {
        return NULL;
    }
    int ox, oy, px, py;
    alias(&ox, &oy, self->chunk_size, x, y);
    alias(&px, &py, self->chunk_size, x + w, y + h);
    PyObject *out = PyList_New(0);
    for(int yes=oy; yes<py+1; yes++) {
        for(int xes=ox; xes<px+1; xes++) {
            PyObject *key = Py_BuildValue("ii", xes, yes);
            World__inflate(self, key, NULL);
            PyObject *cell = get_cell(self, xes, yes);
            PyList_Append(out, cell);
            Py_DECREF(key);
        }
    }
    return out;
}

static PyObject *World_seed(WorldObject *self, PyObject *args) {
    int ix, iy;
    PyObject *sprites;
    if (!PyArg_ParseTuple(args, "iiO", &ix, &iy, &sprites)) {
        return NULL;
    }

    PyObject *iterator = PyObject_GetIter(sprites);
    PyObject *item, *key;

    if (iterator == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "Could not iterate over sprites.");
        return NULL;
    }

    while (item = PyIter_Next(iterator)) {
        // do the stuff here
        PyObject *x = PyObject_GetAttrString(item, "x");
        PyObject *y = PyObject_GetAttrString(item, "y");
        int xx = PyLong_AsLong(x);
        int yy = PyLong_AsLong(y);
        Py_DECREF(x);
        Py_DECREF(y);
        key = Py_BuildValue("iiO", xx, yy, item);
        World_insert(self, key);
        Py_DECREF(item);
        Py_DECREF(key);
    }

    Py_DECREF(iterator);

    if (PyErr_Occurred()) {
        return NULL;
    }
    key = Py_BuildValue("ii", ix, iy);
    PyDict_SetItem(self->seeded, key, Py_True);
    Py_DECREF(key);
    return Py_None;
}

static PyObject *World_get_batches(WorldObject *self, PyObject *args) {
    int x, y, w, h;
    if (!PyArg_ParseTuple(args, "iiii", &x, &y, &w, &h)) {
        return NULL;
    }
    int ox, oy, px, py;
    alias(&ox, &oy, self->chunk_size, x, y);
    alias(&px, &py, self->chunk_size, x + w, y + h);
    PyObject *out = PyList_New(0);
    for(int yes=oy; yes<py+1; yes++) {
        for(int xes=ox; xes<px+1; xes++) {
            PyObject *key = Py_BuildValue("ii", xes, yes);
            if (PyDict_Contains(self->bg_batches, key)) {
                PyObject *bg_batch = PyDict_GetItem(self->bg_batches, key);
                PyList_Append(out, bg_batch);
                Py_DECREF(bg_batch);
            }
            if (PyDict_Contains(self->batches, key)) {
                // sort bdict later
                PyObject *bdict = PyDict_GetItem(self->batches, key);
                int size = PyDict_Size(bdict);
                PyObject *vals = PyDict_Values(bdict);
                for(int bind=0; bind<size; bind++) {
                    PyObject *batch = PyList_GetItem(vals, bind);
                    PyList_Append(out, batch);
                    Py_DECREF(batch);
                }
                Py_DECREF(vals);
            }
            Py_DECREF(key);
        }
    }
    return out;
}

static PyMemberDef World_members[] = {
    {"chunk_size", T_INT, offsetof(WorldObject, chunk_size), 0,
     "The size of a world chunk"},
    {"world", T_OBJECT_EX, offsetof(WorldObject, world), 0,
     "The actual store of cells."},
    {"seeded", T_OBJECT_EX, offsetof(WorldObject, seeded), 0,
     "Seeded chunks"},
    {"batches", T_OBJECT_EX, offsetof(WorldObject, batches), 0,
     "Chunk batches"},
    {"vertex_lists", T_OBJECT_EX, offsetof(WorldObject, vertex_lists), 0,
     "Chunk vertex_lists"},
    {"bg_batches", T_OBJECT_EX, offsetof(WorldObject, bg_batches), 0,
     "Chunk bg_batches"},
    {"bgs", T_OBJECT_EX, offsetof(WorldObject, bgs), 0,
     "Chunk bgs"},
    {NULL}  /* Sentinel */ };

static PyMethodDef World_methods[] = {
    {"_alias", (PyCFunction) World__alias, METH_VARARGS,
        "Alias a pair of coordinates to a chunk coordinate."},
    {"unseeded", (PyCFunction) World_unseeded, METH_VARARGS,
        "Check if a chunk has been seeded."},
    {"_inflate", (PyCFunction) World__inflate, METH_VARARGS | METH_KEYWORDS,
        "Inflate a chunk before population."},
    {"set_bg", (PyCFunction) World_set_bg, METH_VARARGS,
        "Set background for a chunk."},
    {"insert", (PyCFunction) World_insert, METH_VARARGS,
        "Insert a sprite"},
    {"delete", (PyCFunction) World_delete, METH_VARARGS,
        "Delete a sprite"},
    {"get", (PyCFunction) World_get, METH_VARARGS,
        "Get sprites in an area"},
    {"get_chunks", (PyCFunction) World_get_chunks, METH_VARARGS | METH_KEYWORDS,
        "Get chunks"},
    {"seed", (PyCFunction) World_seed, METH_VARARGS, "Seed a chunk"},
    {"get_batches", (PyCFunction) World_get_batches, METH_VARARGS,
        "Get batches"},
    {NULL}  /* Sentinel */ };

static PyGetSetDef World_getsets[] = {
    //{"right",  /* name */
    //  (getter) World_get_right,
    //  (setter) World_set_right,
    //  NULL,  /* doc */
    //  NULL /* closure */},
    //{"bottom",  /* name */
    //  (getter) World_get_bottom,
    //  (setter) World_set_bottom,
    //  NULL,  /* doc */
    //  NULL /* closure */},
    {NULL}
};

static PyTypeObject WorldType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "rect.World",
    .tp_doc = "The world storage for birch",
    .tp_basicsize = sizeof(WorldObject),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_new = World_new,
    .tp_init = (initproc) World_init,
    .tp_dealloc = (destructor) World_dealloc,
    .tp_members = World_members,
    .tp_methods = World_methods,
    .tp_getset = World_getsets
};

static PyModuleDef world_module = {
    PyModuleDef_HEAD_INIT,
    .m_name = "world",
    .m_doc = "The world storage for birch",
    .m_size = -1,
};

PyMODINIT_FUNC PyInit__world(void)
{
    if (PyType_Ready(&WorldType) < 0)
        return NULL;

    _module = PyModule_Create(&world_module);
    if (_module == NULL)
        return NULL;

    Py_INCREF(&WorldType);
    PyModule_AddObject(_module, "World", (PyObject *) &WorldType);
    graphics = PyImport_ImportModule("pyglet.graphics");
    Batch = PyObject_GetAttrString(graphics, "Batch");
    draw = PyObject_GetAttrString(graphics, "draw");

    return _module;
}

