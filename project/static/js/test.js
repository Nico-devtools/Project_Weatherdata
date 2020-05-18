var elem = document.getElementById("next");
var elem1 = document.getElementById("myForm");
var scrollmenu = getElementById('scrollmenu')
elem.addEventListener("submit", myFunction);
elem1.addEventListener("submit", openModal);

function myFunction() {
  document.getElementById('scrollmenu').scrollLeft += 100;
}

function openModal(){
    ('#myModal').modal('show');
    e.preventDefault();
}

/*
('#myForm').on('submit', function(e){
('#myModal').modal('show');
e.preventDefault();
});
*/