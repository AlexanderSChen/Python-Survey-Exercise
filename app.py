from flask import Flask, request, render_template,  redirect, flash,  jsonify, session, make_response
from surveys import surveys
from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)

app.config['SECRET_KEY'] = "secretsecret"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)

RESPONSES = 'responses'
CURRENT_SURVEY = 'current_survey'

@app.route('/')
def show_pick_survey_form():
    """ Display survey choices for the user to pick"""

    return render_template('survey-choice.html', surveys = surveys)

@app.route('/', methods = ['POST'])
def pick_survey():
    """ user selects which survey they want"""

    survey_id = request.form['survey_code']

    if request.cookies.get(f"completed_{survey_id}"):
        return render_template('backtrack.html')

    survey = surveys[survey_id]
    session[CURRENT_SURVEY] = survey_id

    return render_template('start.html', survey=survey)

@app.route('/begin', methods=['POST'])
def start_survey():
    """ Clear the session of responses"""

    session[RESPONSES] = []

    return redirect('/questions/0')

@app.route('/answer', methods=['POST'])
def handle_question():
    """ Save responses in the session responses and redirect to the next question"""

    choice = request.form['answer']
    text = request.form.get("text", "")

    responses = session[RESPONSES]
    responses.append({"choice": choice, "text": text})

    session[RESPONSES] = responses
    survey_code = session[CURRENT_SURVEY]
    survey = surveys[survey_code]

    if(len(responses) == len(survey.questions)):
        return redirect("/complete")

    else:
        return redirect(f"/questions/{len(responses)}")

@app.route('/questions/<int:qid>')
def show_question(qid):
    """ Display current question"""

    responses = session.get(RESPONSES)
    survey_code = session[CURRENT_SURVEY]
    survey = surveys[survey_code]

    if(responses is None):
        return redirect("/")

    if(len(responses) == len(survey.questions)):
        return redirect('/complete')

    if(len(responses) != qid):
        flash(f"invalid question id: {qid}.")
        return redirect(f"/questions/{len(responses)}")

    question = survey.questions[qid]

    return render_template('survey.html', question_num=qid, question = question)

@app.route('/complete')
def thank_user():
    """Thanks the user for completing the survey and displays the user's answers"""

    survey_id = session[CURRENT_SURVEY]
    survey = surveys[survey_id]
    responses = session[RESPONSES]

    html = render_template('end-of-survey.html', survey=survey, responses = responses)


    response = make_response(html)
    response.set_cookie(f"completed_{survey_id}", 'yes', max_age=60)
    return response