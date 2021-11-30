from website import create_app

app = create_app()

#if we start the main page and nothing else, the main_view template is loaded into the skeleton
@app.route("/")
def open_main():
    #location of the template might have to be specified further in order for the return statement to work
    return render_template('main_view.html')

@app.route("/movie")
def open_movie():
    return render_template('movie_view.html')

    

if __name__ == '__main__':
    app.run(debug=True)
