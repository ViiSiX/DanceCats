// requirements
var gulp = require('gulp');
var gulpBrowser = require("gulp-browser");
var reactify = require('reactify');
var del = require('del');
var size = require('gulp-size');

// task
gulp.task('transform', function () {
  return gulp.src('./app/static/script/jsx/*.js')
    .pipe(gulpBrowser.browserify({transform: ['reactify']}))
    .pipe(gulp.dest('./app/static/script/js/'))
    .pipe(size());
});

gulp.task('del', function () {
  return del(['./app/static/scripts/js']);
});

gulp.task('default', ['del'], function() {
  console.log("Transform JSX to JS!");
  gulp.start('transform');
});