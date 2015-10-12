/*
 * Copyright 2015 University of Denver <http://pardee.du.edu/>
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.datagator.tools.importer.impl;

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.lang.reflect.Constructor;
import java.lang.reflect.InvocationTargetException;
import java.util.HashMap;
import org.apache.commons.io.FilenameUtils;
import org.datagator.tools.importer.AtomType;
import org.datagator.tools.importer.Extractor;
import org.datagator.tools.importer.InputStreamExtractor;

/**
 * Extract data from single local file.
 *
 * @author LIU Yu <liuyu@opencps.net>
 * @date 2015/09/30
 */
public class FileExtractor implements Extractor {

    private static final HashMap<
            String, Constructor<? extends InputStreamExtractor>> factory
            = new HashMap<String, Constructor<? extends InputStreamExtractor>>();

    static {
        try {
            final Constructor<? extends InputStreamExtractor> _csv
                    = CsvInputStreamExtractor.class.getConstructor(
                            InputStream.class);
            factory.put("csv", _csv);
        } catch (NoSuchMethodException e) {
            throw new RuntimeException(e);
        }
    }

    private static Extractor fromFile(File file) throws IOException {
        file = file.getAbsoluteFile();
        if (!file.isFile() || !file.canRead()) {
            throw new IllegalArgumentException(String.format(
                    "invalid file '%s'", file.getPath()));
        }
        try {
            String ext = FilenameUtils.getExtension(file.getAbsolutePath());
            if (!factory.containsKey(ext)) {
                throw new IllegalArgumentException(String.format(
                        "unknown file type '%s'", ext));
            }
            return factory.get(ext).newInstance(new FileInputStream(file));
        } catch (InstantiationException ex) {
            throw new RuntimeException(ex);
        } catch (IllegalAccessException ex) {
            throw new RuntimeException(ex);
        } catch (IllegalArgumentException ex) {
            throw new RuntimeException(ex);
        } catch (InvocationTargetException ex) {
            throw new RuntimeException(ex);
        }
    }

    private final File _file;
    private final Extractor _extractor;
    private int _numRecords = 0;

    public FileExtractor(File file) throws IOException {
        _file = file.getAbsoluteFile();

        final Extractor startGroup = new GroupExtractor.StartGroup() {
            @Override
            public Object getCurrentAtomData() {
                return FilenameUtils.getBaseName(_file.getAbsolutePath());
            }
        };

        final Extractor stopGroup = new GroupExtractor.EndGroup() {
            @Override
            public Object getCurrentAtomData() {
                return _numRecords;
            }
        };

        _extractor = new ChainExtractor(new Extractor[]{
            startGroup, FileExtractor.fromFile(file), stopGroup});
    }

    @Override
    public AtomType nextAtom() throws IOException {
        AtomType token = _extractor.nextAtom();
        if (token != null) {
            if (token.equals(AtomType.END_RECORD)) {
                _numRecords += 1;
            }
        }
        return token;
    }

    @Override
    public AtomType getCurrentAtomType() {
        return _extractor.getCurrentAtomType();
    }

    @Override
    public Object getCurrentAtomData() {
        if (getCurrentAtomType().equals(AtomType.START_RECORD)) {
            return _numRecords; // ordinal # of current record
        }
        return _extractor.getCurrentAtomData();
    }

}
