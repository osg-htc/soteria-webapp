window.onload = function() {
  main();
}

function ResearcherApplicationForm() {
    this.criteria_node = document.getElementById("criteria")

    this.initiate = function(){
        this.criteria_node.addEventListener("change", () => this.change_criteria())
        this.change_criteria()
    }
    this.change_criteria = function(){
        let to_hide = document.getElementsByClassName( "requirement-option")

        for(let i = 0; i < to_hide.length; i++){
            to_hide[i].hidden = true
            let children = to_hide[i].children
            for(let j = 0; j < children.length; j++){
                if(children[j].localName == "input"){
                    children[j].required = false
                }
            }
        }

        active_element = document.getElementById(this.criteria_node.value)
        if(active_element){
            active_element.hidden = false
            let children = active_element.children
            for(let j = 0; j < children.length; j++){
                if(children[j].localName == "input"){
                    children[j].required = true
                }
            }
        }

    }
    this.initiate()
}

function main() {
    const researcher_application_form = new ResearcherApplicationForm()
}
