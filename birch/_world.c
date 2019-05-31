#include </usr/include/python3.6m/Python.h>
#include </usr/include/python3.6m/structmember.h>
#include <stdio.h>
#include "_birch.h"

void World_dealloc(WorldObject *self)
{
    Py_TYPE(self)->tp_free((PyObject *) self);
}

PyObject *World_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    WorldObject *self;
    self = (WorldObject *) type->tp_alloc(type, 0);
    return (PyObject *) self;
}

int World_init(WorldObject *self, PyObject *args, PyObject *kwds)
{
    self->world = PyDict_New();
    self->world_meta = PyDict_New();
    self->seeded = PyDict_New();
    self->batches = PyDict_New();
    self->vertex_lists = PyDict_New();
    self->bg_batches = PyDict_New();
    self->bgs = PyDict_New();
    self->chunk_size = 512;
    return 0;
}

int *alias(int *ox, int *oy, int chunk_size, int x, int y) {
    *ox = (int)floor((double)x / chunk_size);
    *oy = (int)floor((double)y / chunk_size);
    return 0;
}

PyObject *World__alias(WorldObject *self, PyObject *args) {
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

PyObject *World_unseeded(WorldObject *self, PyObject *args) {
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

int inflate(PyObject *dict, int ix, int iy) {
    PyObject *pix = PyLong_FromLong(ix);
    PyObject *piy = PyLong_FromLong(iy);
    PyObject *key = Py_BuildValue("ii", ix, iy);
    PyObject *rdict, *cdict;
    int changed = 0;
    if (!PyDict_Contains(dict, piy)) {
        rdict = PyDict_New();
        PyDict_SetItem(dict, piy, rdict);
        changed = 1;
    } else {
        rdict = PyDict_GetItem(dict, piy);
    }
    if (!PyDict_Contains(rdict, pix)) {
        cdict = PyDict_New();
        PyDict_SetItem(rdict, pix, cdict);
        changed = 1;
    }
    Py_DECREF(pix);
    Py_DECREF(piy);
    Py_DECREF(key);
    return changed;
}


PyObject *World__inflate(WorldObject *self, PyObject *args) {
    int ix, iy;
    int changed;
    PyObject *batch;
    if (!PyArg_ParseTuple(args, "ii", &ix, &iy)) {
        return NULL;
    }
    changed = inflate(self->world, ix, iy);
    PyObject *pix = PyLong_FromLong(ix);
    PyObject *piy = PyLong_FromLong(iy);
    PyObject *key = Py_BuildValue("ii", ix, iy);
    if (changed) {
        batch = PyObject_CallObject(Batch, NULL);
        PyDict_SetItem(self->batches, key, batch);
    }
    Py_DECREF(pix);
    Py_DECREF(piy);
    Py_DECREF(key);
    return Py_None;
}

PyObject *World_set_bg(WorldObject *self, PyObject *args) {
    PyObject *sprite;
    int x, y;
    if (!PyArg_ParseTuple(args, "Oii", &sprite, &x, &y)) {
        return NULL;
    }
    int ox, oy;
    alias(&ox, &oy, self->chunk_size, x, y);
    PyObject *key = Py_BuildValue("ii", ox, oy);
    PyObject *bgbatch;
    if (!PyDict_Contains(self->bg_batches, key)) {
        bgbatch = PyObject_CallObject(Batch, NULL);
        PyDict_SetItem(self->bg_batches, key, bgbatch);
    } else {
        bgbatch = PyDict_GetItem(self->bg_batches, key);
    }
    PyObject_SetAttrString(sprite, "batch", bgbatch);
    char bgs_key[30] = "";
    sprintf(bgs_key, "%d_%d", ox, oy);
    PyDict_SetItemString(self->bgs, bgs_key, sprite);
    Py_DECREF(key);
    return Py_None;
}

PyObject *get_cell(WorldObject *self, int ox, int oy) {
    PyObject *row = PyDict_GetItem(self->world, PyLong_FromLong(oy));
    PyObject *cell = PyDict_GetItem(row, PyLong_FromLong(ox));
    return cell;
}

PyObject *World_move(WorldObject *self, PyObject *args) {
    PyObject *sprite;
    int fx, fy, tx, ty;
    if (!PyArg_ParseTuple(args, "Oiiii", &sprite, &fx, &fy, &tx, &ty)) {
        return NULL;
    }
    int ox, oy, px, py;
    alias(&ox, &oy, self->chunk_size, fx, fy);
    alias(&px, &py, self->chunk_size, tx, ty);

    if (ox != px && oy != py) {
        delete(self, ox, oy, sprite);
        insert(self, px, py, sprite);
    }
    return Py_None;
}

void insert(WorldObject *self, int ox, int oy, PyObject *sprite) {
    PyObject *key = Py_BuildValue("ii", ox, oy);

    World__inflate(self, key);

    PyObject *cell = get_cell(self, ox, oy);
    PyObject *spriteId = PyObject_GetAttrString(sprite, "id");
    PyDict_SetItem(cell, spriteId, sprite);

    PyObject *chunk_batch = PyDict_GetItem(self->batches, key);
    PyObject_SetAttrString(sprite, "batch", chunk_batch);

    Py_DECREF(key);
    Py_DECREF(spriteId);
}


PyObject *World_insert(WorldObject *self, PyObject *args) {
    PyObject *sprite;
    int x, y;
    if (!PyArg_ParseTuple(args, "Oii", &sprite, &x, &y)) {
        return NULL;
    }
    int ox, oy;
    alias(&ox, &oy, self->chunk_size, x, y);
    insert(self, ox, oy, sprite);

    return Py_None;
}

void delete(WorldObject *self, int ox, int oy, PyObject *sprite) {
    PyObject *key = Py_BuildValue("ii", ox, oy);
    World__inflate(self, key);
    PyObject_SetAttrString(sprite, "batch", Py_None);
    PyObject *cell = get_cell(self, ox, oy);

    PyObject *spriteId = PyObject_GetAttrString(sprite, "id");
    PyDict_DelItem(cell, spriteId);
    Py_DECREF(spriteId);

    Py_DECREF(key);
}

PyObject *World_delete(WorldObject *self, PyObject *args) {
    PyObject *sprite;
    int x, y;
    if (!PyArg_ParseTuple(args, "Oii", &sprite, &x, &y)) {
        return NULL;
    }
    int ox, oy;
    alias(&ox, &oy, self->chunk_size, x, y);
    delete(self, ox, oy, sprite);
    return Py_None;
}

PyObject *get_meta(WorldObject *self, int ox, int oy) {
    inflate(self->world_meta, ox, oy);
    PyObject *row = PyDict_GetItem(self->world_meta, PyLong_FromLong(oy));
    PyObject *meta = PyDict_GetItem(row, PyLong_FromLong(ox));
    return meta;
}

PyObject *set_meta(WorldObject *self, PyObject *new_meta, int ox, int oy) {
    inflate(self->world_meta, ox, oy);
    PyObject *row = PyDict_GetItem(self->world_meta, PyLong_FromLong(oy));
    PyDict_SetItem(row, PyLong_FromLong(ox), new_meta);
    return Py_None;
}

PyObject *World_get_meta(WorldObject *self, PyObject *args) {
    PyObject *meta_out;
    int fx, fy;
    if (!PyArg_ParseTuple(args, "ii", &fx, &fy)) {
        return NULL;
    }
    int ox, oy;
    alias(&ox, &oy, self->chunk_size, fx, fy);

    meta_out = get_meta(self, ox, oy);
    return meta_out;
}

PyObject *World_set_meta(WorldObject *self, PyObject *args) {
    int fx, fy;
    PyObject *new_meta;
    if (!PyArg_ParseTuple(args, "Oii", &new_meta, &fx, &fy)) {
        return NULL;
    }
    int ox, oy;
    alias(&ox, &oy, self->chunk_size, fx, fy);

    set_meta(self, new_meta, ox, oy);
    return Py_None;
}

PyObject *World_get_surrounding(WorldObject *self, PyObject *args) {
    PyObject *cell, *cells, *item;
    RectObject *itemrect, *rect;
    if (!PyArg_ParseTuple(args, "OO", &cell, &cells)) {
        return NULL;
    }
    rect = (RectObject *)PyObject_GetAttrString(cell, "rect");
    RectShallow _inflated = {
        .x = rect->x - rect->width,
        .y = rect->y - rect->height,
        .width = rect->width * 3,
        .height = rect->height * 3
    };
    RectShallow *inflated = &_inflated;
    Py_DECREF(rect);
    PyObject *out = PyList_New(0);
    int length = PyList_Size(cells);
    for(int x=0; x<length; x++) {
        item = PyList_GetItem(cells, x);
        itemrect = (RectObject *)PyObject_GetAttrString(cell, "rect");
        if (colliderect(inflated, itemrect)) {
            PyList_Append(out, item);
        }
        Py_DECREF(itemrect);
    }
    return out;
}

PyObject *World_get(WorldObject *self, PyObject *args) {
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
            World__inflate(self, key);
            PyObject *cell = get_cell(self, xes, yes);
            PyObject *cellVals = PyDict_Values(cell);
            PyObject *iterator = PyObject_GetIter(cellVals);
            PyObject *item;

            if (iterator == NULL) {
                continue;
            }

            while (item = PyIter_Next(iterator)) {
                // do the stuff here
                PyObject *args = Py_BuildValue("iiii", x, y, w, h);
                PyObject *res = PyObject_CallMethod(item, "intersects", "iiii", x, y, w, h);
                if (!PySequence_Contains(out, item) && res == Py_True) {
                    PyList_Append(out, item);
                }
                Py_DECREF(args);
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

PyObject *World_get_chunks(WorldObject *self, PyObject *args, PyObject *kwargs) {
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
            World__inflate(self, key);
            PyObject *cell = get_cell(self, xes, yes);
            PyList_Append(out, cell);
            Py_DECREF(key);
        }
    }
    return out;
}

PyObject *World_seed(WorldObject *self, PyObject *args) {
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
        args = Py_BuildValue("iiO", xx, yy, item);
        World_insert(self, args);
        Py_DECREF(item);
        //Py_DECREF(args);
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

PyObject *World_get_batches(WorldObject *self, PyObject *args) {
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
            }
            if (PyDict_Contains(self->batches, key)) {
                PyObject *chunk_batch = PyDict_GetItem(self->batches, key);
                PyList_Append(out, chunk_batch);
            }
            Py_DECREF(key);
        }
    }
    return out;
}

PyMemberDef World_members[] = {
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

PyMethodDef World_methods[] = {
    {"_alias", (PyCFunction) World__alias, METH_VARARGS,
        "Alias a pair of coordinates to a chunk coordinate."},
    {"unseeded", (PyCFunction) World_unseeded, METH_VARARGS,
        "Check if a chunk has been seeded."},
    {"_inflate", (PyCFunction) World__inflate, METH_VARARGS,
        "Inflate a chunk before population."},
    {"set_bg", (PyCFunction) World_set_bg, METH_VARARGS,
        "Set background for a chunk."},
    {"insert", (PyCFunction) World_insert, METH_VARARGS,
        "Insert a sprite"},
    {"delete", (PyCFunction) World_delete, METH_VARARGS,
        "Delete a sprite"},
    {"move", (PyCFunction) World_move, METH_VARARGS,
        "Move a sprite from one cell to another"},
    {"set_meta", (PyCFunction) World_set_meta, METH_VARARGS,
        "Set metadata for a chunk."},
    {"get_meta", (PyCFunction) World_get_meta, METH_VARARGS,
        "Get metadata for a chunk."},
    {"get", (PyCFunction) World_get, METH_VARARGS,
        "Get sprites in an area"},
    {"get_chunks", (PyCFunction) World_get_chunks, METH_VARARGS | METH_KEYWORDS,
        "Get chunks"},
    {"get_surrounding", (PyCFunction) World_get_surrounding, METH_VARARGS,
        "Get cells from an area directly adjacent to the cell, based on its width."},
    {"seed", (PyCFunction) World_seed, METH_VARARGS, "Seed a chunk"},
    {"get_batches", (PyCFunction) World_get_batches, METH_VARARGS,
        "Get batches"},
    {NULL}  /* Sentinel */ };

PyGetSetDef World_getsets[] = {
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

PyTypeObject WorldType = {
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

