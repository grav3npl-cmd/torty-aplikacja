double obliczKosztTortu(
  double bazaCm,
  double targetCm,
  List<dynamic> skladnikiPrzepisu, // Lista z przepisu
  List<dynamic> cenySklepu,        // Lista z magazynu (Firebase)
) {
  // 1. Oblicz współczynnik (tak jak w Twoim kodzie Python)
  double wsp = (targetCm / bazaCm) * (targetCm / bazaCm);
  double kosztTotal = 0.0;

  // 2. Pętla po składnikach
  for (var item in skladnikiPrzepisu) {
    String nazwa = item['nazwa'];
    double ilosc = item['ilosc'];
    
    // Szukamy ceny tego składnika w magazynie
    var produktWsklepie = cenySklepu.firstWhere(
      (e) => e['nazwa'] == nazwa, 
      orElse: () => null
    );

    if (produktWsklepie != null) {
      double cenaOpakowania = produktWsklepie['cena'];
      double wagaOpakowania = produktWsklepie['waga_opakowania'];
      
      // Matematyka z Twojego kodu:
      double cenaZaGram = cenaOpakowania / wagaOpakowania;
      kosztTotal += (cenaZaGram * ilosc * wsp);
    }
  }

  return kosztTotal;
}