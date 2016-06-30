var webpack = require('webpack');

module.exports = [
  {
    name: 'dance-cat-pre',
    entry: {
      Main: './client/js/DanceCat.Main.js',
      Constants: ['./client/js/DanceCat.Constants.js'],
      QueryResults: './client/jsx/DanceCat.QueryResult.js'
    },
    output: {
      path: './DanceCat/static/bundle/',
      filename: 'DanceCat.[name].js',
      library: ['DanceCat', "[name]"],
      libraryTarget: "umd"
    },
    module: {
      loaders: [
        {
          test: /.\/client\/js\/\.js$/,
          loaders: ["babel"],
          query: {
            presets: 'es2015'
          }
        },
        {
          test: /\.css$/,
          loaders: ["style", "css"]
        },
        {
          test: /\.scss$/,
          loaders: ["style", "css", "postcss", "sass"]
        },
        {
          test: /\.less$/,
          loaders: ["style", "css", "less"]
        },
        {
          test: /\.(eot|ttf|svg|gif|png|woff|woff2)$/,
          loader: "file-loader"
        },
        {
          test: /\.js$/,
          loader: 'babel',
          query: {
            presets: ['es2015', 'react']
          }
        }
      ]
    },
    plugins: [
      new webpack.DefinePlugin({
        'process.env':{
          'NODE_ENV': JSON.stringify('production')
        }
      }),
      new webpack.ProvidePlugin({
        $: "jquery",
        jQuery: "jquery",
        io: "socket.io-client",
        React: "react",
        ReactDOM: "react-dom"
      }),
      new webpack.optimize.UglifyJsPlugin({
        compress: { warnings: false }
      })
    ]
  }
];
