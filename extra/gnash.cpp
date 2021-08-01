//
// Created by per on 8/1/21.
//

// gnash.cpp:  Main routine for top-level SWF player, for Gnash.
//
//   Copyright (C) 2005, 2006, 2007, 2008, 2009, 2010,
//   2011, 2014 Free Software Foundation, Inc
//
// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, write to the Free Software
// Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
//

#ifdef HAVE_CONFIG_H
#include "gnashconfig.h"
#endif

#include <string>
#include <iostream>
#include <iterator>
#include <ios>
#include <boost/format.hpp>
#include <boost/program_options.hpp>
#include <boost/algorithm/string/join.hpp>
#include <boost/algorithm/string/split.hpp>
#include <boost/algorithm/string/classification.hpp>
#include <algorithm>
#include <cstdlib>
#include <utility>
#include <functional>

#ifdef ENABLE_NLS
# include <clocale>
#endif

#include "Player.h"
#include "log.h"
#include "rc.h" // for use of rcfile
#include "GnashNumeric.h" // for clamp
#include "GnashException.h"
#include "revno.h"
#include "MediaHandler.h"
#include "GnashFactory.h"
#include "utility.h"
#include "accumulator.h"
#include "GnashFileUtilities.h"

using std::endl;
using std::cout;


std::string url;

namespace gnash {
    class Player;
}

namespace {
    gnash::LogFile& dbglogfile = gnash::LogFile::getDefaultInstance();
    gnash::RcInitFile& rcfile = gnash::RcInitFile::getDefaultInstance();
}

// Forward declarations
namespace {
    namespace po = boost::program_options;
    po::options_description getSupportedOptions(gnash::Player& p);

    void setupSoundAndRendering(gnash::Player& p, int i);
    void setupFlashVars(gnash::Player& p,
                        const std::vector<std::string>& params);
    void setupFDs(gnash::Player& p, const std::string& fds);
    void setupCookiesIn(gnash::Player& p, const std::string& cookiesIn);

    void usage_gui_keys(std::ostream& os);
    void usage(std::ostream& os, const po::options_description& opts);
    void build_options(std::ostream& os);
    void version_and_copyright(std::ostream& os);
}



int main(int argc, char *argv[]){
    auto flash_file = "multitaskgame.swf";


    std::ios::sync_with_stdio(false);
    gnash::Player player;


    // player.setDoRender(false);

    player.setDoSound(rcfile.usePluginSound());
    player.setDoSound(rcfile.useSound());
    player.setFPS(1000);

    try{
        player.run(argc, argv, flash_file);
    }catch (const gnash::GnashException& ex) {
        std::cerr << "Error: " << ex.what() << "\n";
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}

         namespace {

    void
    setupFlashVars(gnash::Player& p, const std::vector<std::string>& params)
    {
        for (std::vector<std::string>::const_iterator i = params.begin(),
                e = params.end(); i != e; ++i) {
            const std::string& param = *i;
            const size_t eq = param.find("=");
            if (eq == std::string::npos) {
                p.setParam(param, "true");
                return;
            }
            const std::string name = param.substr(0, eq);
            const std::string value = param.substr(eq + 1);
            p.setParam(name, value);
        }
    }





    void
    usage_gui_keys(std::ostream& os)
    {
    }

    void
    usage(std::ostream& os, const po::options_description& opts)
    {
    }

    void
    version_and_copyright(std::ostream& os)
    {
    }

    void
    build_options(std::ostream& os)
    {
    }


} // unnamed namespace

