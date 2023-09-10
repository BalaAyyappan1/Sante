const regForm = document.getElementById("reg-form");
const sections = document.getElementsByClassName("session");
let currentStep = 0;

function showStep(step) {
  sections[currentStep].style.display = "none";
  sections[step].style.display = "block";
  currentStep = step;
}

function nextStep() {
  if (currentStep < sections.length - 1) {
    showStep(currentStep + 1);
  }
}

function prevStep() {
  if (currentStep > 0) {
    showStep(currentStep - 1);
  }
}

// Add event listeners to the buttons
document.querySelector("#reg-form button[type='submit']").addEventListener("click", function(event) {
  event.preventDefault();
  regForm.submit();
});
document.querySelector("#reg-form button[type='button'][onclick='nextStep()']").addEventListener("click", nextStep);
document.querySelector("#reg-form button[type='button'][onclick='prevStep()']").addEventListener("click", prevStep);

// Show the first section
showStep(currentStep);
