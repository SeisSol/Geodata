/**
 * @file
 * This file is part of SeisSol.
 *
 * @author Sebastian Rettenberger (sebastian.rettenberger AT tum.de, http://www5.in.tum.de/wiki/index.php/Sebastian_Rettenberger)
 *
 * @section LICENSE
 * Copyright (c) 2016, SeisSol Group
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 * 1. Redistributions of source code must retain the above copyright notice,
 *    this list of conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above copyright notice,
 *    this list of conditions and the following disclaimer in the documentation
 *    and/or other materials provided with the distribution.
 *
 * 3. Neither the name of the copyright holder nor the names of its
 *    contributors may be used to endorse or promote products derived from this
 *    software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF  MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
 * CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
 * SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
 * CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE  USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 *
 * @section DESCRIPTION
 */

#include <map>
#include <string>

#include <netcdf.h>

#include "utils/args.h"
#include "utils/logger.h"
#include "utils/stringutils.h"
#include "utils/timeutils.h"

static void checkNcError(int error)
{
	if (error != NC_NOERR)
		logError() << "An netCDF error occurred:" << nc_strerror(error);
}

template<size_t N>
static void ncPutText(int file, int var, const char* name, const char (&text)[N])
{
	checkNcError(nc_put_att_text(file, var, name, N-1, text));
}

int main(int argc, char* argv[])
{
	utils::Args args;
	args.addOption("chunk-size", 'c', "Chunk size for the new netCDF file (default: 64)", utils::Args::Required, false);
	args.addAdditionalOption("input", "input file");
	args.addAdditionalOption("output", "output file", false);

	switch (args.parse(argc, argv)) {
	case utils::Args::Help:
		return 0;
	case utils::Args::Error:
		return 1;
	}

	std::string input = args.getAdditionalArgument<const char*>("input");

	int ncIFile;
	checkNcError(nc_open(input.c_str(), NC_NOWRITE, &ncIFile));

	// Check number of dimensions
	int ndims, nvars;
	checkNcError(nc_inq(ncIFile, &ndims, &nvars, 0L, 0L));
	if (ndims != 3)
		logError() << "Unsupported number of dimensions found:" << ndims;

	// Get variable IDs
	int* ncIVars = new int[nvars];
	checkNcError(nc_inq_varids(ncIFile, 0L, ncIVars));

	bool isCompound = false;
	std::map<std::string, int> ncIVarMap;
	int ncICoords[3] = {-1, -1, -1};

	for (int i = 0; i < nvars; i++) {
		char varname[NC_MAX_NAME+1];
		checkNcError(nc_inq_varname(ncIFile, ncIVars[i], varname));

		int ncVar;
		checkNcError(nc_inq_varid(ncIFile, varname, &ncVar));

		const std::string name(varname);
		if (name == "x")
			ncICoords[0] = ncVar;
		else if (name == "y")
			ncICoords[1] = ncVar;
		else if (name == "z")
			ncICoords[2] = ncVar;
		else {
			if (name == "data")
				isCompound = true;

			ncIVarMap[name] = ncVar;
		}
	}

	delete [] ncIVars;

	if (isCompound)
		logError() << "Found compound data. Convertion to Paraview is currntly not implemented.";
	else
		logInfo() << "Found compound data not found, converting to SeisSol format.";

	// Get the order of IDs
	std::map<std::string, unsigned int> varOrder;
	varOrder["rho"] = 0;
	varOrder["mu"] = 1;
	varOrder["g"] = 1; // Same as mu
	varOrder["lambda"] = 2;

	std::map<unsigned int, std::string> orderedVars;
	for (std::map<std::string, int>::const_iterator it = ncIVarMap.begin();
			it != ncIVarMap.end(); it++) {
		orderedVars[varOrder.at(it->first)] = it->first;
	}

	// Create new netCDF file
	logInfo() << "Creating ouput file";
	std::string output;
	if (args.isSetAdditional("output"))
		output = args.getAdditionalArgument<const char*>("output");
	else {
		output = input;
		utils::StringUtils::replaceLast(output, ".nc", "");

		if (isCompound)
			output += "_p.nc";
		else
			output += "_s.nc";
	}

	int ncOFile;
	checkNcError(nc_create(output.c_str(), NC_NETCDF4, &ncOFile));
	ncPutText(ncOFile, NC_GLOBAL, "creator", "asagi2paraview");
	std::string timestamp = utils::TimeUtils::timeAsString("%F %T");
	checkNcError(nc_put_att_text(ncOFile, NC_GLOBAL, "created", timestamp.length(), timestamp.c_str()));

	// Copy dimensions
	const char* dims[3] = {"x", "y", "z"};
	size_t dimLength[3];
	int ncODims[3];
	for (unsigned int i = 0; i < 3; i++) {
		int ncIDim;
		checkNcError(nc_inq_dimid(ncIFile, dims[i], &ncIDim));

		checkNcError(nc_inq_dim(ncIFile, ncIDim, 0L, &dimLength[i]));

		checkNcError(nc_def_dim(ncOFile, dims[i], dimLength[i], &ncODims[2-i]));
	}

	// Create variables
	int ncOCoords[3];
	for (unsigned int i = 0; i < 3; i++) {
		checkNcError(nc_def_var(ncOFile, dims[i], NC_FLOAT, 1, &ncODims[2-i], &ncOCoords[i]));
		size_t len;
		if (nc_inq_attlen(ncIFile, ncICoords[i], "units", &len) == NC_NOERR) {
			char* value = new char[len];
			checkNcError(nc_get_att_text(ncIFile, ncICoords[i], "units", value));

			checkNcError(nc_put_att_text(ncOFile, ncOCoords[i], "units", len, value));
			delete [] value;
		}
	}

	size_t chunkSize = args.getArgument<size_t>("chunk-size", 64);
	size_t chunks[3] = {std::min(chunkSize, dimLength[2]),
		std::min(chunkSize, dimLength[1]),
		std::min(chunkSize, dimLength[0])};
	if (chunkSize > 0)
		logInfo() << utils::nospace << "Setting chunk size to (" << chunks[0] << ", " << chunks[1] << ", " << chunks[2] << ")";

	int* ncOVars;
	if (isCompound) {
		ncOVars = 0L;
		// TODO
	} else {
		int ncType;
		checkNcError(nc_def_compound(ncOFile, orderedVars.size()*sizeof(float), "material", &ncType)); // TODO make name dynamic

		unsigned int i = 0;
		for (std::map<unsigned int, std::string>::const_iterator it = orderedVars.begin();
				it != orderedVars.end(); it++, i++) {
			checkNcError(nc_insert_compound(ncOFile, ncType, it->second.c_str(), i*sizeof(float), NC_FLOAT));
		}

		ncOVars = new int[1];
		checkNcError(nc_def_var(ncOFile, "data", ncType,3, ncODims, ncOVars));
		if (chunkSize > 0)
			checkNcError(nc_def_var_chunking(ncOFile, ncOVars[0], NC_CHUNKED, chunks));
	}

	// Copy data
	logInfo() << "Copying data";
	for (unsigned int i = 0; i < 3; i++) {
		float* data = new float[dimLength[i]];

		checkNcError(nc_get_var_float(ncIFile, ncICoords[i], data));
		checkNcError(nc_put_var_float(ncOFile, ncOCoords[i], data));

		delete [] data;
	}

	if (isCompound) {
		// TODO
	} else {
		// TODO copy in chunks
		float* data = new float[dimLength[0]*dimLength[1]*dimLength[2]*orderedVars.size()];
		float* tmp = new float[dimLength[0]*dimLength[1]*dimLength[2]];

		unsigned int i = 0;
		for (std::map<unsigned int, std::string>::const_iterator it = orderedVars.begin();
				it != orderedVars.end(); it++, i++) {
			checkNcError(nc_get_var_float(ncIFile, ncIVarMap.at(it->second), tmp));

			for (unsigned int j = 0; j < dimLength[0]*dimLength[1]*dimLength[2]; j++) {
				data[j*orderedVars.size() + i] = tmp[j];
			}
		}

		delete [] tmp;

		checkNcError(nc_put_var(ncOFile, ncOVars[0], data));

		delete [] data;
	}

	delete [] ncOVars;

	checkNcError(nc_close(ncIFile));
	checkNcError(nc_close(ncOFile));

	return 0;
}
