import React from 'react';
import { StyleSheet, Text, View, ImageBackground, Image, Button, Dimensions} from 'react-native';
import * as Location from 'expo-location';
import * as Permissions from 'expo-permissions';
import Slider from '@react-native-community/slider';


export default class App extends React.Component {
  state= {
    location:null,
    geocode:null,
    risk:null,
    errorMessage:""
  }


  componentDidMount(){
    this.getLocationAsync()
  }
  getLocationAsync = async () => {
    let { status } = await Permissions.askAsync(Permissions.LOCATION);
    if (status !== 'granted') {
      this.setState({
        errorMessage: 'Permission to access location was denied',
      });
    }

    let location = await Location.getCurrentPositionAsync({accuracy:Location.Accuracy.BestForNavigation});
    const { latitude , longitude } = location.coords


    this.getGeocodeAsync({latitude, longitude});
    //this.getRiskFactor(latitude, longitude);
    this.setState({ location: {latitude, longitude}});

  };
  getGeocodeAsync= async (location) => {
    let geocode = await Location.reverseGeocodeAsync(location)
    this.setState({ geocode})
  };


  render(){
    const {location,geocode, errorMessage } = this.state
    var sliderValue = 1
    var riskFactor = null
    const {width, height} = Dimensions.get('window');


    return (
      <ImageBackground  source={require("./assets/bg.jpg")} blurRadius={1} style={styles.container}>
        <View style={styles.overlay}>
          <Image source={require("./assets/marker2.png")} style={{width:100,height:100}} />
          <Text style={styles.heading1}>City:  {geocode  ? `${geocode[0].city} ` :""}</Text>
          <Text style={styles.heading3}>Coordinates:   {location ? `${location.latitude}, ${location.longitude}` :""}</Text>

          <Text style={styles.heading2}>{errorMessage}</Text>
          <Slider
            style = {styles.slider}
            maximumValue={10}
            minimumValue={1}
            minimumTrackTintColor="#FFFFFF"
            maximumTrackTintColor="#000000"
            step={1}
            value={1}
            onSlidingComplete={
               val => this.setState({radius: val})
            }/>
          
          <View style={styles.textCon}>
            <Text style={styles.colorGrey}>{1} km</Text>
            <Text style={styles.colorGrey}>{10} km</Text>
          </View>


          <View style={{top:50}}>
              <Button
                    onPress={async () => {
                             console.log('started');
                             await fetch('https://sccovidapp.ue.r.appspot.com//todo/api/v1.0/tasks', {
                                     method: 'post',
                                     headers: {
                                      'Accept': 'application/json, text/plain, */*',
                                      'Content-Type': 'application/json'
                                     },
                                     body: JSON.stringify({"latitude":location.latitude.toString(),"longitude":location.longitude.toString(),"radius":this.state.radius.toString()})
                                     }).then(res=>res.json())
                                        .then(res => this.setState({risk: res["number_of_tweets"]}));
                      }}

               title="Get Risk Factor"
               color="#000000" 
               styles = {{padding: 115}}/>

              {this.state.risk
                    ? <Text style={styles.result}> Risk Factor: {this.state.risk} </Text>
                    : null
              }
          </View>



        </View>
      </ImageBackground>
    );
  }
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    alignItems: 'center',
    justifyContent: 'center',
    fontFamily: 'serif'
    
  },
  overlay:{
    backgroundColor:"#00000070",
    height:"100%",
    width:"100%",
    justifyContent:"center",
    alignItems:"center"
  },
  slider:{
    width:"75%",
    justifyContent:"center",
    alignItems:"center"
  },
  heading1:{
    color:"#fff",
    fontWeight:"bold",
    fontSize:30,
    margin:20
  },
  heading2:{
    color:"#fff",
    margin:5,
    fontWeight:"bold",
    fontSize:15
  },
  heading3:{
    color:"#fff",
    margin:5
  },
  result:{
    margin:100,
    fontSize:22,
    fontWeight:"bold",
    alignItems:"center",
    color: "#FFFFFF"
  },

  textCon: {
    width: 320,
    flexDirection: 'row',
    justifyContent: 'space-between'
  },
  colorGrey: {
    color: '#d3d3d3'
  },


});

