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
package org.datagator.tools.importer;

import javax.xml.xpath.XPathExpression;
import com.fasterxml.jackson.core.JsonEncoding;
import com.fasterxml.jackson.core.JsonFactory;
import com.fasterxml.jackson.core.JsonGenerator;
import java.io.File;
import java.io.IOException;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.logging.Level;
import java.util.logging.Logger;
import org.apache.commons.cli.CommandLine;
import org.apache.commons.cli.CommandLineParser;
import org.apache.commons.cli.DefaultParser;
import org.apache.commons.cli.HelpFormatter;
import org.datagator.tools.importer.impl.FileExtractor;
import org.datagator.utils.json.StandardPrinter;
import org.apache.commons.cli.Option;
import org.apache.commons.cli.OptionGroup;
import org.apache.commons.cli.Options;
import org.apache.commons.cli.ParseException;
import org.datagator.tools.importer.impl.ChainExtractor;
import org.datagator.tools.importer.impl.GroupExtractor;

/**
 * CLI Interface of DataGator Importer.
 *
 * @author LIU Yu <liuyu@opencps.net>
 * @date 2015/10/02
 */
public class Main {

    private static final Logger log = Logger.getLogger(
            "org.datagator.tools.importer");

    private static final int EX_OK = 0;
    private static final int EX_USAGE = 64;

    private static final JsonFactory json = new JsonFactory();
    private static final CommandLineParser parser = new DefaultParser();
    private static final Options opts = new Options();
    private static final HelpFormatter help = new HelpFormatter();

    private static final Option optGroup = Option.builder("F")
            .longOpt("filter")
            .desc("specify grouping filter as /<foo>/<bar>")
            .type(String.class)
            .required(false)
            .numberOfArgs(1)
            .argName("filter")
            .build();

    private static final Option optLayout = Option.builder("L")
            .longOpt("layout")
            .desc("specify matrix layout as <columnHeaders>,<rowHeaders>")
            .required(false)
            .type(Integer.class)
            .numberOfArgs(2)
            .valueSeparator(',')
            .argName("int>,<int")
            .build();

    private static final Option optHelp = Option.builder("h")
            .longOpt("help")
            .desc("show this help message")
            .build();

    static {
        json.configure(JsonGenerator.Feature.ESCAPE_NON_ASCII, true);
        help.setSyntaxPrefix("Usage: ");
        help.setArgName("input");
        opts.addOption(optGroup).addOption(optLayout).addOption(optHelp);
    }

    public static void main(String[] args) throws IOException {

        int columnHeaders = 0; // cli input
        int rowHeaders = 0; // cli input

        try {
            CommandLine cmds = parser.parse(opts, args);
            if (cmds.hasOption("filter")) {
                throw new UnsupportedOperationException("Not supported yet.");
            }
            if (cmds.hasOption("layout")) {
                String[] layout = cmds.getOptionValues("layout");
                if ((layout == null) || (layout.length != 2)) {
                    throw new IllegalArgumentException("Bad layout.");
                }
                try {
                    columnHeaders = Integer.valueOf(layout[0]);
                    rowHeaders = Integer.valueOf(layout[1]);
                    if ((columnHeaders < 0) || (rowHeaders < 0)) {
                        throw new IllegalArgumentException("Bad layout.");
                    }
                } catch (NumberFormatException ex) {
                    throw new IllegalArgumentException(ex);
                }
            }
            if (cmds.hasOption("help")) {
                help.printHelp("importer", opts, true);
                System.exit(EX_OK);
            }
            // positional arguments, i.e., input file name(s)
            args = cmds.getArgs();
        } catch (ParseException ex) {
            throw new IllegalArgumentException(ex);
        } catch (IllegalArgumentException ex) {
            help.printHelp("importer", opts, true);
            throw ex;
        }

        JsonGenerator jg = json.createGenerator(System.out, JsonEncoding.UTF8);
        jg.setPrettyPrinter(new StandardPrinter());

        final Extractor extractor;

        if (args.length == 1) {
            extractor = new FileExtractor(new File(args[0]));
        } else if (args.length > 1) {
            throw new UnsupportedOperationException("Not supported yet.");
        } else {
            throw new IllegalArgumentException("Missing input.");
        }

        int columnsCount = -1;
        int matrixCount = 0;

        ArrayDeque<String> stack = new ArrayDeque<String>();

        AtomType token = extractor.nextAtom();
        while (token != null) {
            switch (token) {
                case FLOAT:
                case INTEGER:
                case STRING:
                case NULL:
                    jg.writeObject(extractor.getCurrentAtomData());
                    break;
                case START_RECORD:
                    jg.writeStartArray();
                    break;
                case END_RECORD:
                    int _numFields = (Integer) extractor.getCurrentAtomData();
                    if (columnsCount < 0) {
                        columnsCount = _numFields;
                    } else if (columnsCount != _numFields) {
                        throw new RuntimeException(String.format(
                                "row %s has different length than previous rows",
                                String.valueOf(_numFields - 1)));
                    }
                    jg.writeEndArray();
                    break;
                case START_GROUP:
                    stack.push(String.valueOf(extractor.getCurrentAtomData()));
                    jg.writeStartObject();
                    jg.writeStringField("kind", "datagator#Matrix");
                    jg.writeNumberField("columnHeaders", columnHeaders);
                    jg.writeNumberField("rowHeaders", rowHeaders);
                    jg.writeFieldName("rows");
                    jg.writeStartArray();
                    break;
                case END_GROUP:
                    int rowsCount = (Integer) extractor.getCurrentAtomData();
                    if (rowsCount == 0) {
                        jg.writeStartArray();
                        jg.writeEndArray();
                        rowsCount = 1;
                        columnsCount = 0;
                    }
                    jg.writeEndArray();
                    jg.writeNumberField("rowsCount", rowsCount);
                    jg.writeNumberField("columnsCount", columnsCount);
                    jg.writeEndObject();
                    matrixCount += 1;
                    stack.pop();
                    break;
                default:
                    break;
            }
            token = extractor.nextAtom();
        }

        jg.close();

        System.exit(EX_OK);
    }

}
