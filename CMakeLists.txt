cmake_minimum_required(VERSION 3.19)
project(gnash)
list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_LIST_DIR}/cmake")

set(LIBRARY_TYPE STATIC)
# Lock this section so that parallel CMake runs won't clash on checkout in the same directory
file(LOCK ${CMAKE_SOURCE_DIR} DIRECTORY GUARD FILE)

include(cmake/pmm.cmake)
include(cmake/CPM.cmake)

#############################################################################################
#####
##### C++ Compiler Setup
#####
#############################################################################################
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_C_STANDARD 11)
set(LIBRARY_TYPE SHARED)

if (LIBRARY_TYPE STREQUAL "SHARED")
    set(CMAKE_POSITION_INDEPENDENT_CODE ON)
endif ()

if (UNIX)
    set(CMAKE_CXX_COMPILER_LAUNCHER ccache)
endif ()

IF(NOT gcc)
#add_compile_options(-Wdynamic-exception-spec)
endif()



#############################################################################################
#####
##### Gnash - Configuration
#####
#############################################################################################
# Renderer setup
#-M ffmpeg|gst, --media ffmpeg|gst
#The media handler to use (default: ffmpeg).
#.TP
#-R agg|cairo|opengl, --renderer agg|cairo|opengl
#The renderer to use (default: agg).

set(BUILD_AGG "yes")
set(BUILD_OGL "no")
set(BUILD_CAIRO "yes")

set(BUILD_OVG "no")
set(BUILD_GLES "no")
set(BUILD_SDL "yes")



set(RENDERER_LIST "agg cairo")

# HWAcceleration SETUP
set(BUILD_VAAPI "no")
set(BUILD_OMAP "no")
set(HWACCEL_LIST)
if(BUILD_VAAPI STREQUAL "yes")
    list(APPEND HWACCEL_LIST vaapi)
elseif(BUILD_OMAP STREQUAL "yes")
    list(APPEND HWACCEL_LIST omap)
endif()

# Media Setup
# HWAcceleration SETUP
set(BUILD_FFMPEG "no")
set(BUILD_GST "yes")
set(MEDIA_LIST "gstreamer ffmpeg")

add_compile_definitions(VERSION="0.8.11")
add_compile_definitions(BRANCH_NICK="cairl-custom")
add_compile_definitions(BRANCH_REVNO="r21")

add_compile_definitions(COMMIT_ID="master")
add_compile_definitions(GUI_CONFIG="todo")
add_compile_definitions(CONFIG_CONFIG="CaiRL Cmake")
add_compile_definitions(CXXFLAGS="${CMAKE_CXX_FLAGS}") # https://github.com/timretout/gnash/blob/37a2eec77ac64d255c0f64a6cf1fd83ea74e3d70/configure.ac#L765
add_compile_definitions(MEDIA_CONFIG="${MEDIA_LIST}")
add_compile_definitions(HWACCEL_CONFIG="${HWACCEL_LIST}")
add_compile_definitions(RENDERER_CONFIG="${RENDERER_LIST}")
add_compile_definitions(DEFAULT_FLASH_MAJOR_VERSION="10")
add_compile_definitions(DEFAULT_FLASH_MINOR_VERSION="1")
add_compile_definitions(DEFAULT_FLASH_REV_NUMBER="999")
add_compile_definitions(DEFAULT_STREAMS_TIMEOUT=60)
add_compile_definitions(DEFAULT_SOL_SAFEDIR="~/.gnash/SharedObjects")
add_compile_definitions(SYSCONFDIR="~/.gnash") # todo
#add_compile_definitions(ENABLE_SHARED_MEM=0)
add_compile_definitions(HAVE_PNG_H=1)
add_compile_definitions(PLUGINSDIR="~/.gnash/plugins") # todo
if(WIN32)
    add_compile_definitions(DEFAULT_FLASH_PLATFORM_ID="WIN")
    add_compile_definitions(DEFAULT_FLASH_SYSTEM_OS="Windows")
elseif(UNIX)
    add_compile_definitions(DEFAULT_FLASH_PLATFORM_ID="LNX")
    add_compile_definitions(DEFAULT_FLASH_SYSTEM_OS="Linux")
endif()
#############################################################################################
#####
##### VCPKG - Configuration
#####
#############################################################################################
if (WIN32)
    set(VCPKG_TARGET_TRIPLET "x64-windows" CACHE STRING "" FORCE)  # -static ?
    set(VCPKG_STATIC_LINKING ON)
elseif (UNIX)
    set(VCPKG_TARGET_TRIPLET x64-linux)
endif ()

# Also build shared library versions where possible.

#############################################################################################
#####
##### VCPKG - Dependencies
#####
#############################################################################################
set(gnash_dependencies
        giflib
        openssl
        zlib
        freetype
        sdl1
        cairo
        fontconfig
        blend2d

        )

if(BUILD_CAIRO STREQUAL "yes")
    list(APPEND gnash_dependencies cairo)
    add_compile_definitions(RENDERER_CAIRO)
endif()
if(BUILD_CAIRO STREQUAL "yes")

    add_compile_definitions(RENDERER_AGG)
    add_compile_definitions(PIXELFORMAT_RGB555)
    add_compile_definitions(PIXELFORMAT_RGB565)
    add_compile_definitions(PIXELFORMAT_RGB24)
    add_compile_definitions(PIXELFORMAT_BGR24)
    add_compile_definitions(PIXELFORMAT_RGBA32)
    add_compile_definitions(PIXELFORMAT_BGRA32)
    add_compile_definitions(PIXELFORMAT_ARGB32)
    add_compile_definitions(PIXELFORMAT_ABGR32)



endif()


# VCPKG - Install Depedencies
pmm(
        VERBOSE
        DEBUG
        VCPKG
        REVISION master
        REQUIRES ${gnash_dependencies}
        TRIPLET ${VCPKG_TARGET_TRIPLET}
)



find_package(Agg REQUIRED)


find_package(OpenSSL REQUIRED)
find_package(GIF REQUIRED)
find_package(JPEG REQUIRED)
find_package(ZLIB REQUIRED)
find_package(Boost CONFIG  COMPONENTS system program_options REQUIRED)
find_package(freetype CONFIG REQUIRED)
find_package(SDL REQUIRED)
find_package(Fontconfig REQUIRED)
find_package(EXPAT REQUIRED)
find_library(CAIRO_LIBRARIES cairo)
find_library(PIXMAN_LIB pixman-1)
FIND_PACKAGE(PkgConfig REQUIRED)
PKG_CHECK_MODULES(GLIB REQUIRED glib-2.0)


find_library(blend2d_LIBRARY blend2d REQUIRED)
find_path(blend2d_INCLUDES blend2d.h)


find_path(CAIRO_INCLUDE_DIR cairo/cairo.h)
list(APPEND CAIRO_LIBRARIES  ${PIXMAN_LIB}) #


set(gnash_dependency_targets
        ${blend2d_LIBRARY}
        pthread

        ZLIB::ZLIB
        ${Boost_LIBRARIES}
        ${JPEG_LIBRARIES}
        ${SDL_LIBRARIES}
        ${CAIRO_LIBRARIES}
        ${Fontconfig_LIBRARIES}
        ${EXPAT_LIBRARIES}
        ${FREETYPE_LIBRARIES}
        ${PIXMAN_LIB}
        ${LIBAGG_LIBRARIES}
        ${LIBAGGFT2_LIBRARIES}
        ${GSTREAMER_LIBRARIES}
        ${GSTREAMER_BASE_LIBRARIES}
        dl
        ts
)

set(gnash_dependency_includes
        ${blend2d_INCLUDES}
        ${JPEG_INCLUDE_DIR}
        ${SDL_INCLUDE_DIRS}
        ${FREETYPE_INCLUDE_DIRS}
        ${LIBAGG_INCLUDE_DIRS}/agg2
        ${GSTREAMER_INCLUDE_DIRS}
        ${GSTREAMER_BASE_INCLUDE_DIRS}
        ${GLIB_INCLUDE_DIRS}
        )





add_compile_definitions(HAVE_SHMGET)
add_compile_definitions(HAVE_ZLIB_H)
add_compile_definitions(USE_FREETYPE)
add_compile_definitions(SOUND_SDL)
add_compile_definitions(GUI_SDL)
add_compile_definitions(USE_SOUND_SDL)
#add_compile_definitions(USE_MEDIA)
#add_compile_definitions(USE_GST)
#add_compile_definitions(ENABLE_GST_MEDIA)
#add_compile_definitions(USE_GST_ENGINE_TRUE)
#add_compile_definitions(HAVE_FONTCONFIG)
add_compile_definitions(DEFAULT_FONTFILE="/usr/share/fonts/TTF/DejaVuSans.ttf")  # TODO will not work on win

set(gnash_SOURCES
        # Classes that are overwritten
        extra/revno.h
        extra/movie_root.cpp
        extra/Player.cpp
        gnash/gui/NullGui.cpp





        #gnash/libmedia/gst/MediaHandlerGst.cpp
        #gnash/libmedia/gst/MediaParserGst.cpp
        gnash/libmedia/AudioResampler.cpp
        gnash/libmedia/FLVParser.cpp
        gnash/libmedia/MediaHandler.cpp
        gnash/libmedia/AudioDecoderSpeex.cpp
        gnash/libmedia/AudioDecoderSimple.cpp
        gnash/libmedia/MediaParser.cpp


        gnash/libsound/sound_handler.cpp
        gnash/libsound/LiveSound.cpp
        gnash/libsound/StreamingSound.cpp
        gnash/libsound/EmbedSound.cpp
        gnash/libsound/WAVWriter.cpp
        gnash/libsound/StreamingSoundData.cpp
        gnash/libsound/EmbedSoundInst.cpp
        gnash/libsound/sdl/sound_handler_sdl.cpp
        gnash/libsound/sdl/sound_handler_sdl.h



        gnash/librender/agg/Renderer_agg.cpp

        gnash/librender/cairo/Renderer_cairo.cpp
        gnash/librender/cairo/PathParser.cpp
        gnash/gui/sdl/gui_sdl.cpp
        gnash/gui/sdl/sdl.cpp
        gnash/gui/sdl/sdlsup.h
        gnash/gui/sdl/sdl_glue.h
        gnash/gui/sdl/sdl_cairo_glue.cpp
        gnash/gui/sdl/sdl_agg_glue.cpp
        gnash/gui/gui.cpp
        gnash/gui/ScreenShotter.cpp


        gnash/libbase/WallClockTimer.cpp
        gnash/libbase/GnashFileUtilities.cpp
        gnash/libbase/memory.cpp
        gnash/libbase/RTMP.cpp
        gnash/libbase/arg_parser.cpp
        gnash/libbase/NamingPolicy.cpp
        gnash/libbase/GnashImagePng.cpp
        gnash/libbase/tu_file.cpp
        gnash/libbase/NetworkAdapter.cpp
        gnash/libbase/log.cpp
        gnash/libbase/StreamProvider.cpp
        gnash/libbase/GnashImage.cpp
        gnash/libbase/BitsReader.cpp
        gnash/libbase/sharedlib.cpp
        gnash/libbase/IOChannel.cpp
        gnash/libbase/AMF.cpp
        #gnash/libbase/extension.cpp
        gnash/libbase/ClockTime.cpp
        gnash/libbase/GnashImageGif.cpp
        gnash/libbase/GC.cpp
        gnash/libbase/string_table.cpp
        gnash/libbase/URL.cpp
        gnash/libbase/rc.cpp
        gnash/libbase/zlib_adapter.cpp
        gnash/libbase/utf8.cpp
        gnash/libbase/SWFCtype.cpp
        gnash/libbase/GnashImageJpeg.cpp
        gnash/libbase/SharedMem.cpp
        gnash/libbase/noseek_fd_adapter.cpp
        gnash/libbase/Socket.cpp
        gnash/libbase/URLAccessManager.cpp


        gnash/libcore/ExternalInterface.cpp
        gnash/libcore/as_environment.cpp
        gnash/libcore/Video.cpp
        gnash/libcore/DisplayList.cpp
        gnash/libcore/Button.cpp
        gnash/libcore/TextField.cpp
        gnash/libcore/InteractiveObject.cpp
        gnash/libcore/RGBA.cpp
        gnash/libcore/Function2.cpp
        gnash/libcore/SWFRect.cpp
        gnash/libcore/LineStyle.cpp
        gnash/libcore/FillStyle.cpp
        gnash/libcore/PropertyList.cpp
        gnash/libcore/Relay.cpp
        gnash/libcore/Timers.cpp
        gnash/libcore/Geometry.cpp
        gnash/libcore/Shape.cpp
        gnash/libcore/Bitmap.cpp

        gnash/libcore/HostInterface.cpp
        gnash/libcore/MorphShape.cpp
        gnash/libcore/StaticText.cpp
        gnash/libcore/Property.cpp
        gnash/libcore/MovieLoader.cpp
        gnash/libcore/LoadVariablesThread.cpp
        gnash/libcore/ConstantPool.cpp
        gnash/libcore/DynamicShape.cpp
        gnash/libcore/ClassHierarchy.cpp
        gnash/libcore/FreetypeGlyphsProvider.cpp
        gnash/libcore/event_id.cpp
        gnash/libcore/AMFConverter.cpp
        gnash/libcore/namedStrings.cpp
        gnash/libcore/as_value.cpp
        gnash/libcore/CharacterProxy.cpp
        gnash/libcore/BitmapMovie.cpp
        gnash/libcore/SWFMovie.cpp
        gnash/libcore/SWFCxForm.cpp
        gnash/libcore/DisplayObject.cpp
        gnash/libcore/SystemClock.cpp
        gnash/libcore/fontlib.cpp
        gnash/libcore/SWFMatrix.cpp
        gnash/libcore/MovieFactory.cpp
        gnash/libcore/as_object.cpp
        gnash/libcore/DisplayObjectContainer.cpp
        gnash/libcore/MovieClip.cpp
        gnash/libcore/Function.cpp
        gnash/libcore/Font.cpp
        gnash/libcore/SWFStream.cpp
        gnash/libcore/as_function.cpp
        #gnash/libcore/abc/Namespace.cpp
        #gnash/libcore/abc/CodeStream.cpp
        #gnash/libcore/abc/Method.cpp
        #gnash/libcore/abc/AbcBlock.cpp
        #gnash/libcore/abc/Class.cpp
        #gnash/libcore/abc/as_class.cpp
        #gnash/libcore/abc/abc_function.cpp
        gnash/libcore/asobj/System_as.cpp
        gnash/libcore/asobj/Stage_as.cpp
        gnash/libcore/asobj/NetStream_as.cpp
        gnash/libcore/asobj/Boolean_as.cpp
        gnash/libcore/asobj/Sound_as.cpp
        gnash/libcore/asobj/Object.cpp
        gnash/libcore/asobj/XML_as.cpp
        gnash/libcore/asobj/Number_as.cpp
        gnash/libcore/asobj/MovieClipLoader.cpp
        gnash/libcore/asobj/Global_as.cpp
        gnash/libcore/asobj/Camera_as.cpp
        gnash/libcore/asobj/PlayHead.cpp
        gnash/libcore/asobj/TextFormat_as.cpp
        gnash/libcore/asobj/Mouse_as.cpp
        gnash/libcore/asobj/ASConversions.cpp
        gnash/libcore/asobj/XMLSocket_as.cpp
        gnash/libcore/asobj/ContextMenuItem_as.cpp
        gnash/libcore/asobj/TextSnapshot_as.cpp
        gnash/libcore/asobj/LoadVars_as.cpp
        gnash/libcore/asobj/Function_as.cpp
        gnash/libcore/asobj/Error_as.cpp
        gnash/libcore/asobj/Video_as.cpp
        gnash/libcore/asobj/NetConnection_as.cpp
        gnash/libcore/asobj/MovieClip_as.cpp
        gnash/libcore/asobj/Microphone_as.cpp
        gnash/libcore/asobj/SharedObject_as.cpp
        gnash/libcore/asobj/String_as.cpp
        gnash/libcore/asobj/AsBroadcaster.cpp
        gnash/libcore/asobj/Date_as.cpp
        gnash/libcore/asobj/TextField_as.cpp
        gnash/libcore/asobj/ContextMenu_as.cpp
        gnash/libcore/asobj/Array_as.cpp
        gnash/libcore/asobj/XMLNode_as.cpp
        gnash/libcore/asobj/LocalConnection_as.cpp
        gnash/libcore/asobj/Key_as.cpp
        gnash/libcore/asobj/Color_as.cpp
        gnash/libcore/asobj/Selection_as.cpp
        gnash/libcore/asobj/Math_as.cpp
        gnash/libcore/asobj/Accessibility_as.cpp
        gnash/libcore/asobj/LoadableObject.cpp
        gnash/libcore/asobj/flash/flash_pkg.cpp
        gnash/libcore/asobj/flash/net/FileReference_as.cpp
        gnash/libcore/asobj/flash/net/FileReferenceList_as.cpp
        gnash/libcore/asobj/flash/net/net_pkg.cpp
        gnash/libcore/asobj/flash/filters/ColorMatrixFilter_as.cpp
        gnash/libcore/asobj/flash/filters/BitmapFilter_as.cpp
        gnash/libcore/asobj/flash/filters/BevelFilter_as.cpp
        gnash/libcore/asobj/flash/filters/DropShadowFilter_as.cpp
        gnash/libcore/asobj/flash/filters/GradientGlowFilter_as.cpp
        gnash/libcore/asobj/flash/filters/ConvolutionFilter_as.cpp
        gnash/libcore/asobj/flash/filters/BlurFilter_as.cpp
        gnash/libcore/asobj/flash/filters/DisplacementMapFilter_as.cpp
        gnash/libcore/asobj/flash/filters/GlowFilter_as.cpp
        gnash/libcore/asobj/flash/filters/filters_pkg.cpp
        gnash/libcore/asobj/flash/filters/GradientBevelFilter_as.cpp
        gnash/libcore/asobj/flash/display/BitmapData_as.cpp
        gnash/libcore/asobj/flash/display/display_pkg.cpp
        gnash/libcore/asobj/flash/text/TextRenderer_as.cpp
        gnash/libcore/asobj/flash/text/text_pkg.cpp
        gnash/libcore/asobj/flash/external/ExternalInterface_as.cpp
        gnash/libcore/asobj/flash/external/external_pkg.cpp
        gnash/libcore/asobj/flash/geom/Matrix_as.cpp
        gnash/libcore/asobj/flash/geom/Rectangle_as.cpp
        gnash/libcore/asobj/flash/geom/Point_as.cpp
        gnash/libcore/asobj/flash/geom/ColorTransform_as.cpp
        gnash/libcore/asobj/flash/geom/geom_pkg.cpp
        gnash/libcore/asobj/flash/geom/Transform_as.cpp
        gnash/libcore/parser/SWFMovieDefinition.cpp
        gnash/libcore/parser/sprite_definition.cpp
        gnash/libcore/parser/BitmapMovieDefinition.cpp
        gnash/libcore/parser/action_buffer.cpp
        gnash/libcore/parser/SWFParser.cpp
        gnash/libcore/parser/TypesParser.cpp
        gnash/libcore/parser/filter_factory.cpp
        gnash/libcore/parser/sound_definition.cpp
        #gnash/libcore/vm/Machine.cpp
        gnash/libcore/vm/ActionExec.cpp
        gnash/libcore/vm/ASHandlers.cpp
        gnash/libcore/vm/CallStack.cpp
        gnash/libcore/vm/VM.cpp
        gnash/libcore/swf/DefineButtonSoundTag.cpp
        gnash/libcore/swf/DefineScalingGridTag.cpp
        gnash/libcore/swf/DefineBitsTag.cpp
        gnash/libcore/swf/StartSoundTag.cpp
        gnash/libcore/swf/SWF.cpp
        gnash/libcore/swf/SoundInfoRecord.cpp
        gnash/libcore/swf/DefineTextTag.cpp
        gnash/libcore/swf/VideoFrameTag.cpp
        gnash/libcore/swf/TextRecord.cpp
        gnash/libcore/swf/DefineVideoStreamTag.cpp
        gnash/libcore/swf/tag_loaders.cpp
        gnash/libcore/swf/DefineFontTag.cpp
        gnash/libcore/swf/ShapeRecord.cpp
        gnash/libcore/swf/DefineButtonTag.cpp
        gnash/libcore/swf/StreamSoundBlockTag.cpp
        gnash/libcore/swf/CSMTextSettingsTag.cpp
        gnash/libcore/swf/DefineShapeTag.cpp
        gnash/libcore/swf/PlaceObject2Tag.cpp
        gnash/libcore/swf/DefineMorphShapeTag.cpp
        gnash/libcore/swf/DefaultTagLoaders.cpp
        gnash/libcore/swf/DefinitionTag.cpp
        gnash/libcore/swf/SetTabIndexTag.cpp
        gnash/libcore/swf/DefineFontAlignZonesTag.cpp
        gnash/libcore/swf/SoundStreamHeadTag.cpp
        gnash/libcore/swf/DefineButtonCxformTag.cpp
        gnash/libcore/swf/RemoveObjectTag.cpp
        gnash/libcore/swf/TagLoadersTable.cpp
        gnash/libcore/swf/DefineEditTextTag.cpp


        extra/gnashconfig.h)



add_library(gnash_libs STATIC ${gnash_SOURCES})
target_include_directories(gnash_libs PUBLIC
        ${CAIRO_INCLUDE_DIR}/cairo

        extra

        #gnash/libmedia/gst
        #gnash/libmedia

        gnash/librender/cairo
        gnash/librender/agg
        gnash/gui/sdl
        gnash/libcore/asobj/flash/filters
        gnash/libcore/asobj/flash
        gnash/libcore/asobj
        gnash/libcore/swf
        gnash/librender
        gnash/libmedia
        gnash/libcore/swf
        gnash/libcore/vm
        gnash/libcore/parser
        gnash/libbase
        gnash/libcore
        gnash/libsound
        gnash/gui
        ${gnash_dependency_includes}
)
target_link_libraries(
        gnash_libs
        PUBLIC
        ${gnash_dependency_targets}
)


add_executable(gnash_executable extra/gnash.cpp)
target_link_libraries(
        gnash_executable PUBLIC gnash_libs
)