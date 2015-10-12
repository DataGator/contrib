/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package org.datagator.api.client;

import com.fasterxml.jackson.core.JsonGenerator;
import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.core.JsonToken;
import com.fasterxml.jackson.core.type.TypeReference;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.RandomAccessFile;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.NoSuchElementException;
import org.datagator.api.client.Entity;
import org.datagator.api.client.RowBuffer;

/**
 * Spooled row buffer implementation
 *
 * @author LIU Yu <liuyu@opencps.net>
 * @date 2015/09/09
 */
public class SpooledRowBuffer
    implements RowBuffer
{

    private final ArrayList<Object[]> cache;
    private final RandomAccessFile cacheFile;
    private final int cacheLimit;
    private int rowsCount = 0;

    public SpooledRowBuffer(int cacheLimit)
        throws IOException
    {
        this.cache = new ArrayList<Object[]>();
        File tempFile = File.createTempFile("dg_Cache_", ".tmp");
        tempFile.deleteOnExit();
        this.cacheFile = new RandomAccessFile(tempFile, "rw");
        this.cacheLimit = cacheLimit;
    }

    public SpooledRowBuffer()
        throws IOException
    {
        this(1000);
    }

    @Override
    public int size()
    {
        return rowsCount;
    }

    @Override
    public Iterator<Object[]> iterator()
    {
        if (rowsCount <= cacheLimit) {
            return this.cache.iterator();
        } else {
            try {
                flush();
            } catch (IOException ex) {
                throw new RuntimeException(ex);
            }
            return new Iterator<Object[]>()
            {

                private final JsonParser jp;
                private int rowIndex = 0;
                private final TypeReference<ArrayList<Object>> tr
                    = new TypeReference<ArrayList<Object>>()
                    {
                    };

                {
                    try {
                        // TODO lock cache file
                        cacheFile.seek(0);
                        FileReader reader = new FileReader(cacheFile.getFD());
                        jp = Entity.json.createParser(reader);
                        JsonToken token = jp.nextToken(); // START_ARRAY
                        if (!token.equals(JsonToken.START_ARRAY)) {
                            throw new RuntimeException("Corrupted cache file");
                        }
                    } catch (IOException ex) {
                        throw new RuntimeException(ex);
                    }
                }

                @Override
                public boolean hasNext()
                {
                    return rowIndex < rowsCount;
                }

                @Override
                public Object[] next()
                {
                    if (!hasNext()) {
                        throw new NoSuchElementException("No such elememnt.");
                    }
                    try {
                        rowIndex += 1;
                        ArrayList<Object> buffer = jp.readValueAs(tr);
                        return buffer.toArray();
                    } catch (IOException ex) {
                        throw new RuntimeException(ex);
                    }
                }

                @Override
                public void remove()
                {
                    throw new UnsupportedOperationException("Not supported yet.");
                }

            };
        }
    }

    @Override
    public void put(Object[] row)
    {
        cache.add(row);
        if (cache.size() >= cacheLimit) {
            try {
                flush();
            } catch (IOException ex) {
                throw new RuntimeException(ex);
            }
        }
    }

    public void flush()
        throws IOException
    {
        if (cacheFile.length() > 0) {
            cacheFile.seek(cacheFile.length() - 1);
        } else {
            cacheFile.seek(0);
        }
        FileWriter writer = new FileWriter(cacheFile.getFD());
        JsonGenerator jg = Entity.json.createGenerator(writer);
        if (rowsCount < 0) {
            jg.writeRaw(",\n");
        }
        for (Object[] v : this.cache) {
            jg.writeStartArray();
            for (Object e : v) {
                jg.writeObject(e);
            }
            jg.writeEndArray();
            rowsCount += 1;
        }
        jg.flush();
        this.cache.clear();
    }

    @Override
    public void clear()
    {
        // TODO
        rowsCount = 0;
    }
}
